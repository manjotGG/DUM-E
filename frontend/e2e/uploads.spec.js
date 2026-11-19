import { test, expect } from '@playwright/test';

test('upload log predicts using the saved model and plots named sensors', async ({ page, request }, testInfo) => {
  const errors = []; page.on('pageerror', error => errors.push(error.message));
  const sample = await request.get('/api/engines/sample-log');
  const buffer = await sample.body();
  const expected = await (await request.post('/api/engines/predict', { data: { engine_id: 1, cycle: 31 } })).json();
  await page.goto('/#upload');
  await expect(page.getByRole('heading', { name: 'Upload an engine log', exact: true })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Analyze log & predict', exact: true })).toBeDisabled();
  await page.getByLabel('Choose engine log file').setInputFiles({ name: 'my-engine.csv', mimeType: 'text/csv', buffer });
  await page.getByRole('button', { name: 'Analyze log & predict', exact: true }).click();
  await expect(page.getByRole('heading', { name: '1 engine analyzed', exact: true })).toBeVisible();
  const row = page.getByRole('row').filter({ hasText: 'Engine 1' });
  await expect(row).toContainText(expected.predicted_rul.toFixed(1));
  const explanation = page.getByRole('region', { name: 'Prediction explanation' });
  await expect(explanation.getByRole('heading', { name: 'What influenced this estimate?' })).toBeVisible();
  const lowering = expected.explanation.sensor_contributions.find(sensor => sensor.contribution_cycles < -0.05);
  await explanation.getByRole('button', { name: `Show ${lowering.symbol} sensor readings`, exact: true }).click();
  await expect(page.locator('#upload-sensor-select')).toHaveValue(lowering.key);
  await page.locator('#upload-sensor-select').selectOption('sensor_2');
  await expect(page.getByRole('img', { name: 'LPC outlet temperature · T24 measurements through 31 observed cycles' })).toBeVisible();
  await page.locator('#upload-sensor-select').selectOption('sensor_11');
  await expect(page.getByRole('img', { name: 'HPC outlet static pressure · Ps30 measurements through 31 observed cycles' })).toBeVisible();
  const download = page.waitForEvent('download'); await page.getByRole('button', { name: 'Export predictions' }).click();
  expect((await download).suggestedFilename()).toBe('DUM-E-upload-predictions.csv');
  await page.screenshot({ path: `test-results/upload-${testInfo.project.name}.png`, fullPage: true });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBeTruthy();
  expect(errors).toEqual([]);
});

test('short uploads explain the required history and clear previous results', async ({ page, request }) => {
  const text = await (await request.get('/api/engines/sample-log')).text();
  await page.goto('/#upload');
  await page.getByLabel('Choose engine log file').setInputFiles({ name: 'short.log', mimeType: 'text/plain', buffer: Buffer.from(text.split('\n').slice(0, 15).join('\n')) });
  await page.getByRole('button', { name: 'Analyze log & predict', exact: true }).click();
  await expect(page.getByRole('alert')).toContainText('at least 15 consecutive cycles');
  await expect(page.getByRole('button', { name: 'Export predictions' })).toHaveCount(0);
  await page.getByLabel('Choose engine log file').setInputFiles({ name: 'valid.csv', mimeType: 'text/csv', buffer: Buffer.from(text) });
  await expect(page.getByRole('alert')).toHaveCount(0);
  await page.getByRole('button', { name: 'Analyze log & predict', exact: true }).click();
  await expect(page.getByRole('heading', { name: '1 engine analyzed', exact: true })).toBeVisible();
  await page.getByLabel('Choose engine log file').setInputFiles({ name: 'new.csv', mimeType: 'text/csv', buffer: Buffer.from(text) });
  await expect(page.getByRole('button', { name: 'Export predictions' })).toHaveCount(0);
});

test('performance matrix matches saved evaluation and explains the artifact', async ({ page, request }, testInfo) => {
  const report = await (await request.get('/api/engines/metrics')).json();
  const actual = report.predictions.map(p => p.actual_rul), mean = actual.reduce((a, b) => a + b, 0) / actual.length;
  const r2 = 1 - report.predictions.reduce((s, p) => s + (p.predicted_rul - p.actual_rul) ** 2, 0) / actual.reduce((s, a) => s + (a - mean) ** 2, 0);
  await page.goto('/#performance');
  await expect(page.getByRole('heading', { name: 'Model performance.', exact: true })).toBeVisible();
  await expect(page.getByRole('row').filter({ hasText: 'R² score' })).toContainText(r2.toFixed(4));
  await expect(page.getByRole('row').filter({ hasText: 'Mean absolute error (MAE)' })).toContainText(report.mae.toFixed(2));
  await expect(page.getByText('ml/models/engines/model.joblib', { exact: true })).toBeVisible();
  await expect(page.getByText('ml/engines/train.py', { exact: true })).toBeVisible();
  await page.screenshot({ path: `test-results/performance-${testInfo.project.name}.png`, fullPage: true });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBeTruthy();
});
