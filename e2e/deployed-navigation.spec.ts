import { test, expect } from '@playwright/test';

const BASE_URL = 'https://almost-magic.github.io/socrates-and-donuts';

test.describe('Deployed Site Navigation Test Suite (HashRouter)', () => {
  test('Landing Page - contains all sections', async ({ page }) => {
    await page.goto(BASE_URL + '/');
    await expect(page.locator('h1.text-xl').first()).toBeVisible();
    
    // Check for key sections
    await expect(page.locator('text=It\'s 11pm.')).toBeVisible();
    await expect(page.locator('text=For Practitioners')).toBeVisible();
    await expect(page.locator('text=Enter the Practice Space →')).toBeVisible();
    await expect(page.locator('text=Why It\'s Free')).toBeVisible();
    await expect(page.locator('text=IMPORTANT')).toBeVisible();
  });

  test('The Mirror - shows flow options', async ({ page }) => {
    await page.goto(BASE_URL + '/#/mirror');
    await expect(page.getByRole('heading', { name: 'The Mirror' })).toBeVisible();
    await expect(page.locator('text=I need to make a decision')).toBeVisible();
    await expect(page.locator('text=I\'m angry and about to do something')).toBeVisible();
    await expect(page.locator('text=I\'m hurt and want to say something')).toBeVisible();
    await expect(page.locator('text=I\'m sad and thinking of a big change')).toBeVisible();
    await expect(page.locator('text=I\'m anxious and stuck in my head')).toBeVisible();
    await expect(page.locator('text=Something else is bothering me')).toBeVisible();
  });

  test('The Vault - shows empty state or entries', async ({ page }) => {
    await page.goto(BASE_URL + '/#/vault');
    await expect(page.getByRole('heading', { name: 'The Vault' })).toBeVisible();
    await expect(page.locator('text=Write the angry message. Lock it. Decide tomorrow.')).toBeVisible();
    await expect(page.locator('button:has-text("+ New Vault Entry")')).toBeVisible();
  });

  test('Letter - shows letter writing UI', async ({ page }) => {
    await page.goto(BASE_URL + '/#/letter');
    await expect(page.getByRole('heading', { name: 'Letter You\'ll Never Send' })).toBeVisible();
  });

  test('Weather Map - shows weather map UI', async ({ page }) => {
    await page.goto(BASE_URL + '/#/weather');
    await expect(page.getByRole('heading', { name: 'Emotional Weather Map' })).toBeVisible();
  });

  test('Body Compass - shows body compass UI', async ({ page }) => {
    await page.goto(BASE_URL + '/#/body');
    await expect(page.getByRole('heading', { name: 'Body Compass' })).toBeVisible();
  });

  test('Decision Journal - shows decision journal UI', async ({ page }) => {
    await page.goto(BASE_URL + '/#/decisions');
    await expect(page.getByRole('heading', { name: 'Decision Journal' })).toBeVisible();
  });

  test('Rewriter - shows rewriter UI', async ({ page }) => {
    await page.goto(BASE_URL + '/#/rewriter');
    await expect(page.getByRole('heading', { name: 'Message Rewriter' })).toBeVisible();
  });

  test('Wisdom Feed - shows wisdom feed UI', async ({ page }) => {
    await page.goto(BASE_URL + '/#/wisdom');
    await expect(page.getByRole('heading', { name: 'Wisdom Feed' })).toBeVisible();
  });

  test('Quick Capture - shows capture UI', async ({ page }) => {
    await page.goto(BASE_URL + '/#/capture');
    await expect(page.getByRole('heading', { name: 'Quick Capture' })).toBeVisible();
  });
});
