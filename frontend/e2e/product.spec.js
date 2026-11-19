import { test, expect } from '@playwright/test';

async function navigate(page, label) {
  if (await page.getByRole('button', { name: 'Open navigation', exact: true }).isVisible()) await page.getByRole('button', { name: 'Open navigation', exact: true }).click();
  await page.getByRole('navigation', { name: 'Main navigation' }).getByRole('button', { name: label, exact: true }).click();
}

test('real dataset, prediction, engine changes, and session history', async ({ page, request }, testInfo) => {
  const errors = []; page.on('pageerror', error => errors.push(error.message));
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Overview', exact: true })).toBeVisible();
  await expect(page.getByText('System ready', { exact: true })).toBeVisible();
  await page.screenshot({ path: `test-results/overview-${testInfo.project.name}.png`, fullPage: true });
  await page.getByRole('button', { name: 'Open engine workspace' }).click();
  await expect(page.locator('#engine-select')).toHaveValue('1');
  await expect(page.locator('#cycle-number')).toHaveValue('31');
  await expect(page.getByRole('img', { name: 'LPC outlet temperature · T24 measurements through 31 observed cycles' })).toBeVisible();
  await page.locator('#sensor-select').selectOption('sensor_11');
  await expect(page.getByRole('img', { name: 'HPC outlet static pressure · Ps30 measurements through 31 observed cycles' })).toBeVisible();
  await page.locator('#cycle-number').fill('20');
  await expect(page.getByRole('img', { name: 'HPC outlet static pressure · Ps30 measurements through 20 observed cycles' })).toBeVisible();
  const pending = page.waitForResponse(response => response.url().endsWith('/api/engines/predict') && response.request().method() === 'POST');
  await page.getByRole('button', { name: 'Predict remaining useful life', exact: true }).click();
  const backendResult = await (await pending).json();
  await expect(page.getByTestId('rul-result')).toContainText(backendResult.predicted_rul.toFixed(1));
  const direct = await request.post('/api/engines/predict', { data: { engine_id: 1, cycle: 20 } });
  expect((await direct.json()).predicted_rul).toBe(backendResult.predicted_rul);
  await page.screenshot({ path: `test-results/prediction-${testInfo.project.name}.png`, fullPage: true });
  const downloaded = page.waitForEvent('download'); await page.getByRole('button', { name: 'Download observed sensor history' }).click();
  expect((await downloaded).suggestedFilename()).toContain('through-20.csv');
  await page.locator('#engine-select').selectOption('2');
  await expect(page.locator('#cycle-number')).toHaveValue('49');
  await expect(page.getByTestId('rul-result')).toHaveCount(0);
  await page.getByRole('button', { name: 'Predict remaining useful life', exact: true }).click();
  await expect(page.getByTestId('rul-result')).toBeVisible();
  await navigate(page, 'Overview');
  await expect(page.getByText('2 completed', { exact: true })).toBeVisible();
  await expect(page.getByRole('cell', { name: 'ENG-002' })).toBeVisible();
  expect(errors).toEqual([]);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBeTruthy();
});

test('analytics shows saved evaluation and milling stays inactive', async ({ page, request }, testInfo) => {
  const metrics = await (await request.get('/api/engines/metrics')).json();
  await page.goto('/#analytics');
  await expect(page.getByRole('heading', { name: 'Performance, made visible.' })).toBeVisible();
  await expect(page.getByRole('article').filter({ hasText: 'Mean absolute error' })).toContainText(metrics.mae.toFixed(2));
  await expect(page.getByRole('cell', { name: `${metrics.model_name} SELECTED`, exact: true })).toBeVisible();
  const download = page.waitForEvent('download'); await page.getByRole('button', { name: 'Export evaluation' }).click();
  expect((await download).suggestedFilename()).toBe('DUM-E-FD001-evaluation.json');
  await page.screenshot({ path: `test-results/analytics-${testInfo.project.name}.png`, fullPage: true });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBeTruthy();
  await navigate(page, 'Milling machines');
  await expect(page.getByRole('heading', { name: 'The next module is taking shape.' })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Predict remaining useful life' })).toHaveCount(0);
});

test('prediction loading and API error are visible without a placeholder result', async ({ page }) => {
  await page.goto('/#engines');
  await expect(page.locator('#cycle-number')).toHaveValue('31');
  let release;
  const gate = new Promise(resolve => { release = resolve; });
  await page.route('**/api/engines/predict', async route => { await gate; await route.fulfill({ status: 503, contentType: 'application/json', body: JSON.stringify({ detail: 'Engine model unavailable. Retrain and restart.' }) }); });
  await page.getByRole('button', { name: 'Predict remaining useful life', exact: true }).click();
  await expect(page.getByRole('button', { name: 'Analyzing engine history…' })).toBeDisabled();
  release();
  await expect(page.getByRole('alert')).toContainText('Engine model unavailable');
  await expect(page.getByTestId('rul-result')).toHaveCount(0);
  await expect(page.getByRole('button', { name: 'Predict remaining useful life', exact: true })).toBeEnabled();
});

test('unavailable backend shows a recoverable error', async ({ page }) => {
  await page.route('**/health', route => route.abort('failed'));
  await page.route('**/api/engines*', route => route.abort('failed'));
  await page.goto('/');
  await expect(page.getByRole('alert').first()).toBeVisible();
  await expect(page.getByRole('button', { name: 'Retry', exact: true }).first()).toBeVisible();
  await expect(page.getByText('System degraded', { exact: true })).toBeVisible();
});

test('low-cycle prediction identifies contributing sensors and opens their readings', async ({ page }, testInfo) => {
  await page.goto('/#engines');
  await expect(page.locator('#engine-select')).toHaveValue('1');
  await page.locator('#engine-select').selectOption('100');
  await expect(page.locator('#cycle-number')).toHaveValue('198');
  const pending = page.waitForResponse(response => response.url().endsWith('/api/engines/predict'));
  await page.getByRole('button', { name: 'Predict remaining useful life', exact: true }).click();
  const result = await (await pending).json();
  const reason = page.getByRole('region', { name: 'Prediction explanation' });
  await expect(reason.getByRole('heading', { name: 'Why is the remaining life low?' })).toBeVisible();
  const sensor = result.explanation.sensor_contributions[0];
  expect(sensor.contribution_cycles).toBeLessThan(0);
  await expect(reason).toContainText(sensor.name);
  await expect(reason).toContainText(Math.abs(sensor.contribution_cycles).toFixed(1));
  await page.screenshot({ path: `test-results/low-cycle-${testInfo.project.name}.png`, fullPage: true });
  await reason.getByRole('button', { name: `Show ${sensor.symbol} sensor readings`, exact: true }).click();
  await expect(page.locator('#sensor-select')).toHaveValue(sensor.key);
  await expect(page.locator('#sensor-select')).toBeFocused();
  await page.locator('#cycle-number').fill('197');
  await expect(reason).toHaveCount(0);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBeTruthy();
});
