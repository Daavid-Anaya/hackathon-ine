const { test } = require('node:test');
const assert = require('node:assert/strict');
const { chromium } = require('playwright-core');

async function openCalculator(t) {
  assert.ok(process.env.WEB_URL, 'Ejecuta E01 desde el servicio de pruebas Docker');
  const browser = await chromium.launch({ executablePath: process.env.WEB_BROWSER_PATH });
  t.after(() => browser.close());
  const context = await browser.newContext({ viewport: { width: 320, height: 900 }, reducedMotion: 'reduce', serviceWorkers: 'block' });
  const page = await context.newPage();
  page.setDefaultTimeout(6000);
  const errors = [];
  const external = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
  await context.route('**/*', route => {
    if (new URL(route.request().url()).origin === new URL(process.env.WEB_URL).origin) return route.continue();
    external.push(route.request().url());
    return route.abort();
  });
  t.after(() => {
    assert.deepEqual(errors, []);
    assert.deepEqual(external, []);
  });
  await page.goto(`${process.env.WEB_URL}#/propuestas/E01`);
  await page.getByRole('heading', { name: 'Calculadora de cobertura TCHE', exact: true }).waitFor();
  return {
    page,
    total: page.getByRole('textbox', { name: 'Total de trámites', exact: true }),
    extended: page.getByRole('textbox', { name: 'Trámites en horario extendido', exact: true }),
    result: page.getByRole('status', { name: 'Resultado TCHE' }),
  };
}

test('E01: calcula cobertura con un ejemplo sintético y actualiza el resultado', async t => {
  const { page, total, extended, result } = await openCalculator(t);
  await result.getByText('25.0%', { exact: true }).waitFor();
  await page.getByText('Ejemplo sintético', { exact: true }).waitFor();
  assert.equal(await total.inputValue(), '100');
  assert.equal(await extended.inputValue(), '25');
  for (const [all, extra, expected] of [['300', '100', '33.3%'], ['100', '0', '0.0%'], ['100', '100', '100.0%']]) {
    await total.fill(all);
    await extended.fill(extra);
    await result.getByText(expected, { exact: true }).waitFor();
  }
  assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
  await total.focus();
  assert.notEqual(await total.evaluate(el => getComputedStyle(el).outlineStyle), 'none');
  await page.keyboard.press('Tab');
  assert.equal(await extended.evaluate(el => document.activeElement === el), true);
});

test('E01: distingue ausencia de trámites de cero cobertura y rechaza conteos inválidos', async t => {
  const { total, extended, result } = await openCalculator(t);
  await total.fill('0');
  await extended.fill('0');
  await result.getByText('No aplica', { exact: true }).waitFor();
  await total.fill('100');
  await result.getByText('0.0%', { exact: true }).waitFor();
  const invalid = [
    ['100', '101'], ['0', '1'], ['-1', '0'], ['100', '-1'],
    ['1.5', '0'], ['100', '2.5'], ['', '0'], ['100', ''],
    ['abc', '0'], ['100', '1e2'], ['9007199254740992', '0'],
  ];
  for (const [all, extra] of invalid) {
    await total.fill(all);
    await extended.fill(extra);
    await extended.blur();
    assert.equal(await result.getByText(/%|No aplica/).count(), 0, `${all}/${extra} no debe producir un resultado`);
    assert.equal(await result.textContent(), 'Revisa los datos para calcular la cobertura.');
  }
  assert.equal(await total.getAttribute('aria-invalid'), 'true');
  await total.fill('100');
  await extended.fill('101');
  await extended.blur();
  assert.equal(await extended.getAttribute('aria-invalid'), 'true');
  await result.page().getByText('Los trámites en horario extendido no pueden superar el total.', { exact: true }).waitFor();
  await extended.fill('25');
  await result.getByText('25.0%', { exact: true }).waitFor();
  assert.equal(await extended.getAttribute('aria-invalid'), 'false');
});

test('E01: no guarda los cambios al recargar o salir de la propuesta', async t => {
  const { page, total, extended, result } = await openCalculator(t);
  await total.fill('200');
  await extended.fill('80');
  await result.getByText('40.0%', { exact: true }).waitFor();
  const address = page.url();
  await page.keyboard.press('Enter');
  assert.equal(page.url(), address);
  assert.deepEqual(await page.evaluate(() => [localStorage.length, sessionStorage.length, document.cookie]), [0, 0, '']);
  await page.reload();
  await result.getByText('25.0%', { exact: true }).waitFor();
  await extended.fill('50');
  await result.getByText('50.0%', { exact: true }).waitFor();
  await page.getByRole('link', { name: 'Volver al catálogo', exact: true }).click();
  await page.getByRole('link', { name: /E01.*Flexibilidad en credencialización/ }).click();
  await result.getByText('25.0%', { exact: true }).waitFor();
  assert.equal(await total.inputValue(), '100');
  assert.equal(await extended.inputValue(), '25');
});
