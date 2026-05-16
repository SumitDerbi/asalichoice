# Testing

> Living document. Updated every time a test surface or convention changes.
> Cross-reference: [`docs/api/conventions.md`](../api/conventions.md) §9 (Testing).

## Surfaces

| Surface   | Runner       | Scope                              | Where it lives                       |
| --------- | ------------ | ---------------------------------- | ------------------------------------ |
| Unit/Int. | pytest       | Django apps, services, models      | `backend/tests/`                     |
| Component | Vitest + RTL | Admin-UI components, hooks, stores | `admin-ui/tests/`, `src/**/*.test.*` |
| E2E       | Playwright   | User journeys against built shell  | `admin-ui/e2e/`                      |
| API smoke | Newman       | Postman collections (CI + manual)  | `qa/postman/<group>/`                |

## Quick start

```bash
# everything
./scripts/test-all.sh                 # macOS/Linux/WSL
pwsh ./scripts/test-all.ps1           # Windows

# slices
./scripts/test-all.sh --backend-only
./scripts/test-all.sh --frontend-only
./scripts/test-all.sh --no-e2e --no-postman
```

Equivalent `make` targets exist for \*nix: `make test`, `make test-backend`,
`make test-frontend`, `make test-e2e`, `make test-postman`.

## Backend (pytest)

- **Config**: `backend/pytest.ini` + `backend/.coveragerc`. Default run is fast
  (no `--cov`); add `--cov` (or use `scripts/test-all.*`) for the coverage gate.
- **Coverage gate**: 70% lines (`fail_under = 70`).
- **Settings**: `config.settings.development` (SQLite if `DB_PASSWORD` is empty).
- **Markers**: `slow`, `integration`, `e2e` — declared in `pytest.ini`. Add new
  markers there to keep `--strict-markers` happy.

### Fixtures (`backend/tests/conftest.py`)

| Fixture                | Purpose                                                  |
| ---------------------- | -------------------------------------------------------- |
| `user_factory`         | Cheap user creator; pass `password=...` for a real hash. |
| `api_client`           | DRF `APIClient`; pass a user to force-authenticate.      |
| `branch_id`            | Placeholder int until M01 ships `Branch`.                |
| `push_request_context` | Context-manager binder for `RequestContext`.             |
| `capture_audit`        | Returns audit rows created during the test.              |

### Factories (`backend/tests/factories.py`)

```python
from tests.factories import UserFactory, StaffUserFactory, SuperUserFactory

def test_thing(db):
    user = UserFactory(password="hunter2-test")
    staff = StaffUserFactory()
    admin = SuperUserFactory()
```

- `UserFactory` uses `factory.Sequence` for unique emails.
- Default password is unusable; pass `password="..."` for `check_password`.
- Real `BranchFactory` lands with M01; the `branch_factory(id)` stub
  returns an int so branch-scoped tests have something to bind against.

### Gotchas

- **PASSWORD_HASHERS override**: argon2 isn't always available locally; tests that
  check passwords decorate **each test** with
  `@override_settings(PASSWORD_HASHERS=["...PBKDF2PasswordHasher"])` — putting it
  in `pytestmark` raises `TypeError` (pytest expects only `Mark` instances).
- **DRF throttles**: `DEFAULT_THROTTLE_RATES` is snapshotted at class creation;
  override via `monkeypatch.setattr(LoginRateThrottle, 'THROTTLE_RATES', ...)`
  instead of `override_settings`.

## Admin-UI (Vitest + RTL)

- **Config**: `admin-ui/vitest.config.ts`.
- **Setup**: `admin-ui/tests/setup.ts` — jsdom polyfills (`matchMedia`,
  `ResizeObserver`, `scrollIntoView`) + MSW server lifecycle.
- **Coverage gate** (`vitest.config.ts` → `test.coverage.thresholds`):
  lines/statements/branches 70%, functions 65%. Components in
  `src/components/ui/**` are excluded (shadcn primitives).

### Shared helpers (`admin-ui/src/test/`)

| Module              | What it gives you                                            |
| ------------------- | ------------------------------------------------------------ |
| `utils.tsx`         | `renderWithProviders(<X/>, { initialEntries, queryClient })` |
| `mocks/handlers.ts` | Default MSW handlers (auth/login, /me, /refresh, /logout)    |
| `mocks/server.ts`   | `setupServer(...handlers)` — started in `tests/setup.ts`     |

```tsx
import { renderWithProviders, screen } from "@/test/utils";
import { server } from "@/test/mocks/server";
import { http, HttpResponse } from "msw";

it("shows the welcome banner", async () => {
  server.use(
    http.get("http://localhost:8000/api/v1/users/me/", () =>
      HttpResponse.json({ id: 1, name: "Admin" }),
    ),
  );
  renderWithProviders(<Welcome />);
  expect(await screen.findByText(/welcome, admin/i)).toBeInTheDocument();
});
```

The test env pins `VITE_API_BASE_URL` to `http://localhost:8000/api/v1` (via
`vitest.config.ts`); align MSW handler URLs with that base.

### Forms package tests

See [`docs/ui/forms.md`](../ui/forms.md) for the canonical examples covering
schemas, `mapApiErrorToFields`, and `InlineEditCell`.

## E2E (Playwright)

- **Config**: `admin-ui/playwright.config.ts`. `baseURL` from `E2E_BASE_URL`.
- **Fixture**: `admin-ui/e2e/fixtures/auth.ts` exports an `authedPage` fixture
  that walks through `/login` after stubbing `/auth/login/` and `/auth/me/`.

```ts
import { test, expect } from "./fixtures/auth";

test("lands on dashboard", async ({ authedPage }) => {
  await expect(
    authedPage.getByRole("heading", { name: /dashboard/i }),
  ).toBeVisible();
});
```

Run locally against a running `vite dev`:

```bash
npm run dev --workspace admin-ui   # in one shell
npm run e2e --workspace admin-ui   # in another
```

## API smoke (Newman)

- **Collections**: `qa/postman/<group>/collection.json` (one per module).
- **Envs**: `qa/postman/local.env.json`, `qa/postman/staging.env.json`.
- **Runner**: `scripts/postman-run.mjs` walks every group and runs newman via
  `npx --yes newman` (no permanent dependency).

```bash
npm run postman                 # local env
npm run postman:staging         # staging env
node scripts/postman-run.mjs --group auth   # single group
```

Requires the backend to be reachable at `baseUrl`. The unified runner treats
postman failures as **non-blocking** so a missing dev server doesn't tank the
full suite — CI should run postman as a discrete step instead.

## CI orchestration

`scripts/test-all.{sh,ps1}` is the single source of truth. CI should:

1. Install Python + Node deps.
2. `scripts/test-all.sh --no-e2e --no-postman` for the fast lane.
3. Spin up the dev server (and a fixture-loaded DB) for a separate e2e job.
4. Run `node scripts/postman-run.mjs --env staging` in the smoke job.

## Adding a new test surface

1. Wire the runner config under the owning workspace.
2. Add a sample test that proves the surface works.
3. Append to `scripts/test-all.*` so it joins the unified flow.
4. Update this doc + the matrix above.
