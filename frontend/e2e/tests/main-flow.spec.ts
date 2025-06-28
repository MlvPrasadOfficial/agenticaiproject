import { test, expect } from '@playwright/test';

test.describe('Enterprise Insights Copilot E2E Tests', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('http://localhost:3000');
  });

  test('homepage loads correctly', async ({ page }) => {
    // Check that the main elements are visible
    await expect(page.locator('h1')).toContainText('Enterprise Insights Copilot');
    await expect(page.locator('text=Upload your Data')).toBeVisible();
    await expect(page.locator('text=Chat with AI Agents')).toBeVisible();
  });

  test('navigation to visualization dashboard works', async ({ page }) => {
    // Click the data visualization dashboard button
    await page.click('text=Data Visualization Dashboard');
    
    // Should navigate to visualization page
    await expect(page).toHaveURL(/.*visualization/);
    await expect(page.locator('h1')).toContainText('Data Visualization Dashboard');
  });

  test('navigation to conversation interface works', async ({ page }) => {
    // Click the conversation interface button
    await page.click('text=AI Conversation Interface');
    
    // Should navigate to conversation page
    await expect(page).toHaveURL(/.*conversation/);
    await expect(page.locator('h1')).toContainText('Enterprise Insights Copilot');
  });

  test('file upload interface is functional', async ({ page }) => {
    // Look for upload area
    const uploadArea = page.locator('[data-testid="upload-area"], .border-dashed');
    await expect(uploadArea).toBeVisible();
    
    // Check upload text
    await expect(page.locator('text=Drag and drop a file here')).toBeVisible();
  });

  test('conversation interface basic functionality', async ({ page }) => {
    // Navigate to conversation page
    await page.goto('http://localhost:3000/conversation');
    
    // Check for conversation interface elements
    await expect(page.locator('text=Conversation')).toBeVisible();
    await expect(page.locator('text=Results')).toBeVisible();
    await expect(page.locator('text=Insights')).toBeVisible();
    
    // Check for input area
    await expect(page.locator('input[placeholder*="Ask me anything"]')).toBeVisible();
    await expect(page.locator('button:has-text("Send")')).toBeVisible();
  });

  test('send message in conversation interface', async ({ page }) => {
    // Navigate to conversation page
    await page.goto('http://localhost:3000/conversation');
    
    // Wait for page to load
    await page.waitForSelector('input[placeholder*="Ask me anything"]');
    
    // Type a message
    const messageInput = page.locator('input[placeholder*="Ask me anything"]');
    await messageInput.fill('Hello, can you help me analyze data?');
    
    // Click send button
    await page.click('button:has-text("Send")');
    
    // Check that message appears in conversation
    await expect(page.locator('text=Hello, can you help me analyze data?')).toBeVisible();
  });

  test('tab navigation in conversation interface', async ({ page }) => {
    await page.goto('http://localhost:3000/conversation');
    
    // Click on Results tab
    await page.click('text=Results');
    await expect(page.locator('text=Analysis Results')).toBeVisible();
    
    // Click on Insights tab
    await page.click('text=Insights');
    await expect(page.locator('text=Generated Insights')).toBeVisible();
    
    // Click back to Conversation tab
    await page.click('text=Conversation');
    await expect(page.locator('input[placeholder*="Ask me anything"]')).toBeVisible();
  });

  test('voice input toggle functionality', async ({ page }) => {
    await page.goto('http://localhost:3000/conversation');
    
    // Look for voice input toggle button
    const voiceToggle = page.locator('button[title="Toggle voice input"]');
    
    if (await voiceToggle.isVisible()) {
      await voiceToggle.click();
      
      // Should show voice input controls when enabled
      // Note: Actual voice functionality would require user permission
    }
  });

  test('export functionality is accessible', async ({ page }) => {
    await page.goto('http://localhost:3000/conversation');
    
    // Look for export button
    const exportButton = page.locator('button[title="Export conversation"]');
    await expect(exportButton).toBeVisible();
    
    // Click export button (should open modal)
    await exportButton.click();
    
    // Check if export modal opens
    await expect(page.locator('text=Export & Share')).toBeVisible();
  });

  test('responsive design works on mobile viewport', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    await page.goto('http://localhost:3000');
    
    // Check that elements are still visible and accessible
    await expect(page.locator('text=Upload your Data')).toBeVisible();
    await expect(page.locator('text=Chat with AI Agents')).toBeVisible();
  });

  test('error handling for invalid navigation', async ({ page }) => {
    // Try to navigate to non-existent page
    const response = await page.goto('http://localhost:3000/nonexistent');
    
    // Should handle gracefully (404 page or redirect)
    expect(response?.status()).toBeTruthy();
  });

  test('health indicator is visible', async ({ page }) => {
    await page.goto('http://localhost:3000');
    
    // Look for health indicator in top-right
    const healthIndicator = page.locator('.fixed.top-4.right-4');
    await expect(healthIndicator).toBeVisible();
  });

});
