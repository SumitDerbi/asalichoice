/**
 * Playwright fixture that returns a logged-in `page` by stubbing both the
 * login + me endpoints and walking the real login form.
 *
 * Usage:
 *
 *   import { test, expect } from './fixtures/auth';
 *
 *   test('something', async ({ authedPage }) => {
 *     await authedPage.goto('/');
 *     ...
 *   });
 *
 * Why not pre-seed `localStorage`? Because the admin shell calls
 * `bootstrap()` on mount and re-reads the user from `/auth/me/`; routing
 * the response is cleaner than racing the store hydrate.
 */

import { test as base, expect, type Page } from '@playwright/test';

export const SAMPLE_USER = {
  id: 1,
  email: 'admin@example.test',
  mobile: '',
  name: 'Admin',
  display_name: 'Admin',
  is_staff: true,
  is_superuser: true,
  is_active: true,
  date_joined: '2025-01-01T00:00:00Z',
};

export async function loginViaForm(page: Page): Promise<void> {
  await page.route('**/api/v1/auth/login/', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        access: 'access.jwt.token',
        refresh: 'refresh.jwt.token',
        user: SAMPLE_USER,
      }),
    });
  });
  await page.route('**/api/v1/auth/me/', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(SAMPLE_USER),
    });
  });

  await page.goto('/login');
  await page.getByLabel(/^email$/i).fill('admin@example.test');
  await page.getByLabel(/password/i).fill('correct-horse');
  await page.getByRole('button', { name: /sign in/i }).click();
  await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible();
}

export const test = base.extend<{ authedPage: Page }>({
  authedPage: async ({ page }, use) => {
    await loginViaForm(page);
    await use(page);
  },
});

export { expect };
