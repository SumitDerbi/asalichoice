/**
 * Mock Service Worker request handlers shared by Vitest tests.
 *
 * Modules can extend this list via `server.use(...moduleHandlers)` inside a
 * test or `beforeEach` to override the default response for a single case.
 *
 * Conventions:
 * - Handlers stay close to the API conventions in `docs/api/conventions.md`
 *   (envelope `{ error: { code, message, details } }` for errors).
 * - Default `baseUrl` is read from `VITE_API_BASE_URL` (Vite injects it into
 *   tests via the standard `import.meta.env` shim).
 */

import { http, HttpResponse } from 'msw';

const BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1';

export const defaultUser = {
  id: 1,
  email: 'admin@example.test',
  name: 'Admin User',
  display_name: 'Admin User',
  is_staff: true,
  is_superuser: true,
};

export const handlers = [
  http.post(`${BASE}/auth/login/`, async ({ request }) => {
    const body = (await request.json()) as { email?: string; password?: string };
    if (body.email === defaultUser.email && body.password === 'correct-password') {
      return HttpResponse.json({
        access: 'test-access-token',
        refresh: 'test-refresh-token',
        user: defaultUser,
      });
    }
    return HttpResponse.json(
      {
        error: {
          code: 'API-400',
          message: 'Invalid email or password.',
          details: { fields: { email: 'Invalid credentials.' } },
        },
      },
      { status: 400 },
    );
  }),

  http.get(`${BASE}/auth/me/`, () => HttpResponse.json(defaultUser)),

  http.post(`${BASE}/auth/refresh/`, () => HttpResponse.json({ access: 'new-access-token' })),

  http.post(`${BASE}/auth/logout/`, () => new HttpResponse(null, { status: 205 })),
];
