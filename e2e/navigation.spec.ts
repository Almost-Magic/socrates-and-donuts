import { test, expect } from '@playwright/test';

test.describe('Navigation Test Suite', () => {
  test('Landing Page - contains all sections', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('h1')).toContainText('Socrates & Donuts');
    
    // Check for key sections
    await expect(page.locator('text=It\'s 11pm.')).toBeVisible();
    await expect(page.locator('text=For Practitioners')).toBeVisible();
    await expect(page.locator('text=Enter the Practice Space →')).toBeVisible();
    await expect(page.locator('text=Why It\'s Free')).toBeVisible();
    await expect(page.locator('text=IMPORTANT')).toBeVisible();
  });

  test('The Mirror - shows flow options', async ({ page }) => {
    await page.goto('/mirror');
    await expect(page.locator('h1')).toContainText('The Mirror');
    await expect(page.locator('text=I need to make a decision')).toBeVisible();
    await expect(page.locator('text=I\'m angry and about to do something')).toBeVisible();
    await expect(page.locator('text=I\'m hurt and want to say something')).toBeVisible();
    await expect(page.locator('text=I\'m sad and thinking of a big change')).toBeVisible();
    await expect(page.locator('text=I\'m anxious and stuck in my head')).toBeVisible();
    await expect(page.locator('text=Something else is bothering me')).toBeVisible();
  });

  test('The Vault - shows empty state or entries', async ({ page }) => {
    await page.goto('/vault');
    await expect(page.locator('h1')).toContainText('The Vault');
    await expect(page.locator('text=Write the angry message. Lock it. Decide tomorrow.')).toBeVisible();
    await expect(page.locator('button:has-text("+ New Vault Entry")')).toBeVisible();
  });

  test('Letter - shows letter writing UI', async ({ page }) => {
    await page.goto('/letter');
    await expect(page.locator('h1')).toContainText('Letter');
  });

  test('Weather Map - shows weather map UI', async ({ page }) => {
    await page.goto('/weather');
    await expect(page.locator('h1')).toContainText('Weather');
  });

  test('Body Compass - shows body compass UI', async ({ page }) => {
    await page.goto('/body');
    await expect(page.locator('h1')).toContainText('Body');
  });

  test('Decision Journal - shows decision journal UI', async ({ page }) => {
    await page.goto('/decisions');
    await expect(page.locator('h1')).toContainText('Decision');
  });

  test('Rewriter - shows rewriter UI', async ({ page }) => {
    await page.goto('/rewriter');
    await expect(page.locator('h1')).toContainText('Rewriter');
  });

  test('Wisdom Feed - shows wisdom feed UI', async ({ page }) => {
    await page.goto('/wisdom');
    await expect(page.locator('h1')).toContainText('Wisdom');
  });

  test('Quick Capture - shows capture UI', async ({ page }) => {
    await page.goto('/capture');
    await expect(page.locator('h1')).toContainText('Capture');
  });
});
