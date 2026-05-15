import { expect, test } from '@playwright/test';

const SAMPLE_USER = {
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

test.describe('Login flow', () => {
  test('shows a validation error when email is empty', async ({ page }) => {
    await page.goto('/login');
    await page.getByRole('button', { name: /sign in/i }).click();
    await expect(page.getByText(/valid email/i)).toBeVisible();
  });

  test('logs in successfully and lands on the dashboard', async ({ page }) => {
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

    await page.goto('/login');
    await page.getByLabel(/^email$/i).fill('admin@example.test');
    await page.getByLabel(/password/i).fill('correct-horse');
    await page.getByRole('button', { name: /sign in/i }).click();

    await expect(page).toHaveURL(/\/$/);
    await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible();
  });

  test('surfaces the API error message on bad credentials', async ({ page }) => {
    await page.route('**/api/v1/auth/login/', async (route) => {
      await route.fulfill({
        status: 400,
        contentType: 'application/json',
        body: JSON.stringify({
          error: { code: 'API-400', message: 'Invalid email or password.' },
        }),
      });
    });

    await page.goto('/login');
    await page.getByLabel(/^email$/i).fill('admin@example.test');
    await page.getByLabel(/password/i).fill('wrong');
    await page.getByRole('button', { name: /sign in/i }).click();

    await expect(page.getByText(/invalid email or password/i)).toBeVisible();
    await expect(page).toHaveURL(/\/login/);
  });
});
