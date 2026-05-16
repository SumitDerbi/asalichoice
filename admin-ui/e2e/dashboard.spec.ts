import { expect, test } from './fixtures/auth';

test.describe('Dashboard', () => {
  test('shows the dashboard heading inside the shell', async ({ authedPage }) => {
    await expect(authedPage.getByRole('heading', { name: /dashboard/i })).toBeVisible();
    await expect(authedPage.locator('aside[aria-label="Primary navigation"]')).toBeVisible();
  });

  test('navigates to masters via the sidebar', async ({ authedPage }) => {
    await authedPage
      .getByRole('link', { name: /masters/i })
      .first()
      .click();
    await expect(authedPage).toHaveURL(/\/masters$/);
    await expect(authedPage.getByRole('heading', { name: /masters/i })).toBeVisible();
  });
});
