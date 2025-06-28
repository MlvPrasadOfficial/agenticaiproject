import { test, expect } from '@playwright/test';

test.describe('Enterprise Insights Copilot - Basic Flow', () => {
  test('should load homepage successfully', async ({ page }) => {
    await page.goto('/');
    
    // Check that the page loads
    await expect(page).toHaveTitle(/Enterprise Insights Copilot/);
    
    // Check for main navigation elements
    await expect(page.locator('text=Enterprise Insights Copilot')).toBeVisible();
  });

  test('should display upload interface', async ({ page }) => {
    await page.goto('/');
    
    // Check for file upload area
    await expect(page.locator('text=Upload your Data')).toBeVisible();
    await expect(page.locator('text=Drag and drop a file here')).toBeVisible();
  });

  test('should display agent workflow panel', async ({ page }) => {
    await page.goto('/');
    
    // Check for agent workflow visualization
    await expect(page.locator('text=Agent Workflow')).toBeVisible();
    await expect(page.locator('text=Multi-agent AI system')).toBeVisible();
  });

  test('should display chat interface', async ({ page }) => {
    await page.goto('/');
    
    // Check for chat interface
    await expect(page.locator('text=Ask Copilot')).toBeVisible();
    await expect(page.locator('placeholder=Ask me anything about your data')).toBeVisible();
  });

  test('should have working health check', async ({ page, request }) => {
    // Test backend health endpoint
    const response = await request.get('http://localhost:8000/health');
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data.status).toBe('healthy');
    expect(data).toHaveProperty('timestamp');
    expect(data).toHaveProperty('version');
  });

  test('should handle file upload interaction', async ({ page }) => {
    await page.goto('/');
    
    // Click on upload area
    await page.locator('text=Drag and drop a file here').click();
    
    // Should trigger file input (we won't actually upload in this test)
    // Just verify the interaction works
    await expect(page.locator('input[type="file"]')).toBeHidden(); // File input is typically hidden
  });

  test('should handle query input', async ({ page }) => {
    await page.goto('/');
    
    // Test query input
    const queryInput = page.locator('placeholder=Ask me anything about your data');
    await queryInput.fill('What are the sales trends?');
    
    // Check that input was filled
    await expect(queryInput).toHaveValue('What are the sales trends?');
    
    // Test send button (won't actually send without data)
    const sendButton = page.locator('text=Send Query');
    await expect(sendButton).toBeVisible();
  });

  test('should display system status', async ({ page }) => {
    await page.goto('/');
    
    // Look for system status indicator
    // This might show "Offline" if backend isn't running in test
    await expect(page.locator('text=System')).toBeVisible();
  });

  test('should be responsive on different screen sizes', async ({ page }) => {
    // Test desktop
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto('/');
    await expect(page.locator('text=Enterprise Insights Copilot')).toBeVisible();

    // Test tablet
    await page.setViewportSize({ width: 768, height: 1024 });
    await expect(page.locator('text=Enterprise Insights Copilot')).toBeVisible();

    // Test mobile (this is a desktop app, but should still be viewable)
    await page.setViewportSize({ width: 375, height: 667 });
    await expect(page.locator('text=Enterprise Insights Copilot')).toBeVisible();
  });

  test('should have proper accessibility features', async ({ page }) => {
    await page.goto('/');
    
    // Check for proper heading structure
    const h1 = page.locator('h1');
    await expect(h1).toBeVisible();
    
    // Check for keyboard navigation support
    await page.keyboard.press('Tab');
    // Should focus on interactive elements
    
    // Check for ARIA labels on interactive elements
    const uploadArea = page.locator('[role="button"]').first();
    if (await uploadArea.isVisible()) {
      await expect(uploadArea).toHaveAttribute('aria-label');
    }
  });
});
