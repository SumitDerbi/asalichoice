import { test, expect } from '@playwright/test';

const BASE_URL = process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:5173';
const _API_URL = process.env.PLAYWRIGHT_API_URL || 'http://localhost:8000/api/v1';

test.describe('Auth Flows', () => {
  test('Login by email identifier', async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);
    await page.fill('input[name="identifier"]', 'admin@example.test');
    await page.fill('input[name="password"]', 'pw');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(BASE_URL + '/');
    await expect(page.locator('text=Dashboard')).toBeVisible();
  });

  test('Login by mobile identifier', async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);
    await page.fill('input[name="identifier"]', '9111111111');
    await page.fill('input[name="password"]', 'pw');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(BASE_URL + '/');
  });

  test('Login by employee code', async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);
    await page.fill('input[name="identifier"]', 'EMP-001');
    await page.fill('input[name="password"]', 'pw');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(BASE_URL + '/');
  });

  test('Lockout after failed attempts', async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);
    for (let i = 0; i < 5; i++) {
      await page.fill('input[name="identifier"]', 'admin@example.test');
      await page.fill('input[name="password"]', 'wrongpw');
      await page.click('button[type="submit"]');
      await page.waitForTimeout(200); // debounce
    }
    await expect(page.locator('text=Too many failed attempts')).toBeVisible();
  });

  test('Role-based access gating', async ({ page }) => {
    // This assumes a user with no access to /masters
    await page.goto(`${BASE_URL}/login`);
    await page.fill('input[name="identifier"]', 'limited@example.test');
    await page.fill('input[name="password"]', 'pw');
    await page.click('button[type="submit"]');
    await page.goto(`${BASE_URL}/masters`);
    await expect(page.locator('text=Access denied')).toBeVisible();
  });
});
