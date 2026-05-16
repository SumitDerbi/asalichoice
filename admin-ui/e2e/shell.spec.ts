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

async function login(page: import('@playwright/test').Page) {
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

test.describe('Admin shell', () => {
  test('Ctrl+K opens the command palette', async ({ page }) => {
    await login(page);
    await page.keyboard.press('Control+K');
    await expect(page.getByPlaceholder(/type a command or search/i)).toBeVisible();
  });

  test('? opens the shortcuts overlay', async ({ page }) => {
    await login(page);
    await page.keyboard.press('Shift+/');
    await expect(page.getByRole('heading', { name: /keyboard shortcuts/i })).toBeVisible();
  });

  test('branch switcher persists across reload', async ({ page }) => {
    await login(page);
    await page.getByRole('button', { name: /switch branch/i }).click();
    await page.getByRole('menuitem', { name: /warehouse 1/i }).click();
    await expect(page.getByRole('button', { name: /switch branch/i })).toContainText('WH1');

    await page.reload();
    await expect(page.getByRole('button', { name: /switch branch/i })).toContainText('WH1');
  });

  test('sidebar collapses with the menu button', async ({ page }) => {
    await login(page);
    const sidebar = page.locator('aside[aria-label="Primary navigation"]');
    await expect(sidebar).toHaveClass(/w-60/);
    await page.getByRole('button', { name: /toggle sidebar/i }).click();
    await expect(sidebar).toHaveClass(/w-16/);
  });
});
