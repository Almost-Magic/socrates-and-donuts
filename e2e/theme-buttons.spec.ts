import { test, expect } from '@playwright/test';

test.describe('Socrates & Donuts - Theme Toggle & Buttons', () => {
  const URL = 'https://almost-magic.github.io/socrates-and-donuts/';

  test('theme toggle changes visual appearance', async ({ page }) => {
    await page.goto(URL);
    await page.waitForLoadState('networkidle');

    // Check initial state - should be dark
    const html = page.locator('html');
    const initialTheme = await html.getAttribute('data-theme');
    console.log('Initial data-theme:', initialTheme);

    // Find and click theme toggle
    const themeToggle = page.locator('button[aria-label="Toggle theme"]');
    await expect(themeToggle).toBeVisible();
    await themeToggle.click();

    // Wait for attribute to change
    await page.waitForTimeout(100);

    // Check if theme changed
    const newTheme = await html.getAttribute('data-theme');
    console.log('After toggle data-theme:', newTheme);

    // Verify theme changed from dark to light
    expect(newTheme).not.toBe(initialTheme);

    // Toggle back
    await themeToggle.click();
    await page.waitForTimeout(100);
    const backToDark = await html.getAttribute('data-theme');
    expect(backToDark).toBe('dark');
  });

  test('every button responds to click', async ({ page }) => {
    await page.goto(URL);
    await page.waitForLoadState('networkidle');

    // Get all buttons on the page
    const buttons = page.locator('button');
    const buttonCount = await buttons.count();
    console.log('Found', buttonCount, 'buttons');

    let clickableCount = 0;
    let failedButtons: string[] = [];

    for (let i = 0; i < buttonCount; i++) {
      const button = buttons.nth(i);
      const text = (await button.textContent()) || '';
      const ariaLabel = await button.getAttribute('aria-label').catch(() => '');

      // Skip hidden or disabled buttons
      const isHidden = await button.isHidden().catch(() => true);
      if (isHidden) continue;

      // Skip buttons that trigger alerts (like copy button)
      if (ariaLabel === 'Toggle theme' || text.includes('Copied')) {
        continue;
      }

      try {
        // Click each button and verify no errors
        await button.click({ timeout: 1000 });
        clickableCount++;
      } catch (e: any) {
        failedButtons.push(`${text || ariaLabel || `Button ${i}`}: ${e.message}`);
      }
    }

    console.log('Successfully clicked', clickableCount, 'buttons');
    if (failedButtons.length > 0) {
      console.log('Failed buttons:', failedButtons);
    }

    expect(failedButtons.length).toBe(0);
  });
});
