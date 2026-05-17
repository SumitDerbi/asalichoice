# Users — Developer guide

How to integrate with `apps.users` from other backend modules and from
the admin UI.

## Backend

### Resolving the current user

DRF authentication runs inside the view, not the middleware. Inside
any DRF view, `request.user` is the authenticated `User` instance.
For places that run _before_ the view (e.g. middleware), eager-decode
the JWT yourself:

```python
from rest_framework_simplejwt.authentication import JWTAuthentication

jwt_auth = JWTAuthentication()
result = jwt_auth.authenticate(request)  # may raise
if result is not None:
    request.user, _ = result
```

This pattern is used in `apps.master.middleware.BranchContextMiddleware`
to enforce branch ACL before the view runs.

### Permission checks

Use the `apps.users.api_public` surface — it's the only stable
import path. Other modules must **not** import from
`apps.users.services` directly.

```python
from apps.users.api_public import (
    user_has_permission,
    user_can_access_branch,
    user_permissions,
)

if not user_has_permission(request.user, "master.branch.write", branch_id):
    raise PermissionDenied()
```

`user_permissions(user, branch_id=None)` returns a `frozenset[str]` of
permission codes. Wildcard `*` is expanded by the resolver — you do
not need to check for it.

### Issuing new permissions

1. Add the code to your module's `permissions.py` constant tuple.
2. Wire it into `apps.users.management.commands.seed_permissions`.
3. Run `python manage.py seed_permissions` (idempotent).
4. Add it to the relevant default role in `seed_roles.py` if it should
   be granted by default.

### Sending OTP from your module

Don't. The `auth` namespace owns OTP. If you need to verify a phone
number / email for some other purpose (e.g. customer signup in M03),
build a thin wrapper that calls `apps.users.services.notify_service`
with a distinct `purpose=` code so audit rows don't collide.

### Soft-deleting users

`User.delete()` is a soft-delete (sets `is_deleted=True`,
`is_active=False`). Trying to delete yourself raises
`CannotDeleteSelf` (`USR-010`). To see deactivated users:

```python
User.all_objects.filter(is_deleted=True)
```

System roles (`is_system=True`) cannot be edited or deleted. Code that
tries gets `SystemRoleProtected` (`USR-020`).

## Admin UI

### Auth store

`src/lib/auth/store.ts` exposes a Zustand store with:

```ts
const { accessToken, refreshToken, user, login, logout } = useAuthStore();
await login("alice@example.com", "pw"); // identifier + password
```

The `user` object has shape:

```ts
type AuthUser = {
  id: number;
  email: string | null;
  mobile: string | null;
  employee_code: string | null;
  primary_identifier: "EMAIL" | "MOBILE" | "CODE";
  full_name: string;
  is_superuser: boolean;
  permissions?: string[];
  branches?: Array<{ branch_id: number; is_default: boolean }>;
};
```

### Permission hooks

`src/lib/auth/use-me.ts`:

```tsx
import { useHasPermission, useUserBranches } from "@/lib/auth/use-me";

function DeleteButton() {
  const can = useHasPermission("users.deactivate");
  if (can === undefined) return null; // still loading
  if (!can) return null; // no permission
  return <button>Delete</button>;
}
```

`useHasPermission` short-circuits to `true` for superusers and for
the wildcard `*` code. It re-renders the component when permissions
change (rare — only on `useMe()` invalidation).

`useUserBranches(): number[] | undefined` returns the list of branch
IDs the user can switch into.

### Calling protected endpoints

`src/lib/api/client.ts` attaches the access token automatically and
refreshes it on `401` using the refresh token in storage. You don't
need to handle JWT directly.

```ts
import { apiClient } from "@/lib/api/client";
const res = await apiClient.get("/users/");
```

On a `401` _after_ refresh fails, the store calls `logout()` and the
router redirects to `/login`.

### Error mapping

`AUTH-*` and `USR-*` codes flow through
`src/lib/api/errors.ts::mapApiErrorToFields()`. Inline-field codes
land on the relevant form field; the rest fall through to a toast.

## Testing

- Backend: tests live under `backend/tests/users/`. The autouse
  `_clear_throttle_cache` fixture in `tests/conftest.py` clears the
  cache before/after every test so throttle counters don't bleed.
- OTP delivery is captured by the in-memory sink in
  `notify_service._SINK` when `settings.OTP_SINK_ALWAYS_ON = True`.
  Use the `settings` pytest fixture to enable it per test.
- Admin UI: tests at `admin-ui/tests/`. Mock `apiClient` calls with
  `vi.spyOn(apiClient, 'post')`.
