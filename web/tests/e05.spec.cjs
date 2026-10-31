const { test } = require('node:test');
const assert = require('node:assert/strict');
const { chromium } = require('playwright-core');

const criteria = [
  'Acceso a nivel o con rampa funcional', 'Mampara adaptada', 'Lupa de aumento',
  'Plantilla Braille', 'Atención preferencial', 'Sillas y sombra',
];

async function openChecklist(t) {
  assert.ok(process.env.WEB_URL, 'Ejecuta E05 desde el servicio de pruebas Docker');
  const browser = await chromium.launch({ executablePath: process.env.WEB_BROWSER_PATH });
  t.after(() => browser.close());
  const context = await browser.newContext({ viewport: { width: 320, height: 900 }, reducedMotion: 'reduce', serviceWorkers: 'block' });
  const page = await context.newPage();
  page.setDefaultTimeout(6000);
  const errors = [];
  const external = [];
  await context.route('**/*', route => {
    if (new URL(route.request().url()).origin === new URL(process.env.WEB_URL).origin) return route.continue();
    external.push(route.request().url());
    return route.abort();
  });
  page.on('pageerror', error => errors.push(error.message));
  page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
  t.after(() => {
    assert.deepEqual(errors, []);
    assert.deepEqual(external, []);
  });
  await page.goto(`${process.env.WEB_URL}#/propuestas/E05`);
  await page.getByRole('heading', { name: 'Lista de verificación de accesibilidad', exact: true }).waitFor();
  return {
    page,
    conditions: page.getByRole('group', { name: 'Condiciones de la sede ficticia' }),
    summary: page.getByRole('status', { name: 'Resumen de condiciones' }),
    actions: page.getByRole('region', { name: 'Barreras y acciones pendientes', exact: true }),
  };
}

test('E05: distingue condiciones presentes, ausentes y pendientes sin certificar la sede', async t => {
  const { page, conditions, summary, actions } = await openChecklist(t);
  await page.getByText('Sede ficticia de ejemplo', { exact: true }).waitFor();
  assert.equal(await conditions.getByRole('combobox').count(), 6);
  assert.equal(await summary.textContent(), 'Presentes: 0. Ausentes: 0. Pendientes de verificar: 6.');
  for (const label of criteria) {
    const field = conditions.getByRole('combobox', { name: label, exact: true });
    assert.equal(await field.inputValue(), 'pending');
    await field.selectOption('absent');
    assert.equal(await summary.textContent(), 'Presentes: 0. Ausentes: 1. Pendientes de verificar: 5.');
    const item = actions.getByRole('listitem').filter({ has: page.getByRole('heading', { name: label, exact: true }) });
    await item.getByText('Barrera declarada en el escenario', { exact: true }).waitFor();
    await field.selectOption('present');
    assert.equal(await actions.getByRole('heading', { name: label, exact: true }).count(), 0);
    assert.equal(await summary.textContent(), 'Presentes: 1. Ausentes: 0. Pendientes de verificar: 5.');
    await field.selectOption('pending');
    await item.getByText('Condición por verificar', { exact: true }).waitFor();
  }
  for (const field of await conditions.getByRole('combobox').all()) await field.selectOption('present');
  assert.equal(await summary.textContent(), 'Presentes: 6. Ausentes: 0. Pendientes de verificar: 0.');
  await actions.getByRole('heading', { name: 'Sin pendientes en este ejemplo', exact: true }).waitFor();
  assert.equal(await actions.getByRole('listitem').count(), 0);
  await page.getByText('No equivale a certificar accesibilidad ni a aprobar una sede real.', { exact: true }).waitFor();
  for (const field of await conditions.getByRole('combobox').all()) await field.selectOption('absent');
  assert.equal(await actions.getByRole('listitem').count(), 6);
  assert.equal(await summary.textContent(), 'Presentes: 0. Ausentes: 6. Pendientes de verificar: 0.');
  assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
});

test('E05: permite completar la lista con teclado y anuncia un resumen sin puntuación', async t => {
  const { page, conditions, summary } = await openChecklist(t);
  const fields = conditions.getByRole('combobox');
  let reached = false;
  for (let n = 0; n < 16; n++) {
    await page.keyboard.press('Tab');
    if (await fields.first().evaluate(el => el === document.activeElement)) { reached = true; break; }
  }
  assert.ok(reached);
  for (let index = 0; index < criteria.length; index++) {
    if (index) await page.keyboard.press('Tab');
    assert.equal(await fields.nth(index).evaluate(el => el === document.activeElement), true);
    assert.notEqual(await fields.nth(index).evaluate(el => getComputedStyle(el).outlineStyle), 'none');
    await page.keyboard.press('ArrowUp');
    await page.keyboard.press('ArrowUp');
    assert.equal(await fields.nth(index).inputValue(), 'present');
  }
  assert.equal(await summary.textContent(), 'Presentes: 6. Ausentes: 0. Pendientes de verificar: 0.');
  assert.equal(await summary.getAttribute('aria-live'), 'polite');
  assert.equal(await summary.getAttribute('aria-atomic'), 'true');
  await page.getByText('El resumen cuenta respuestas del ejemplo; no es una puntuación de accesibilidad ni el indicador CEAF.', { exact: true }).waitFor();
});

test('E05: restablece todas las condiciones pendientes al recargar o salir, sin guardar datos', async t => {
  const { page, conditions, summary } = await openChecklist(t);
  const address = page.url();
  await conditions.getByRole('combobox', { name: criteria[0], exact: true }).selectOption('absent');
  await conditions.getByRole('combobox', { name: 'Plantilla Braille', exact: true }).selectOption('present');
  assert.equal(page.url(), address);
  assert.deepEqual(await page.evaluate(() => [localStorage.length, sessionStorage.length, document.cookie]), [0, 0, '']);
  await page.reload();
  await summary.waitFor();
  assert.equal(await summary.textContent(), 'Presentes: 0. Ausentes: 0. Pendientes de verificar: 6.');
  await conditions.getByRole('combobox', { name: criteria[0], exact: true }).selectOption('present');
  await page.getByRole('link', { name: 'Volver al catálogo', exact: true }).click();
  await page.getByRole('link', { name: /E05.*Accesibilidad universal/ }).click();
  assert.equal(await summary.textContent(), 'Presentes: 0. Ausentes: 0. Pendientes de verificar: 6.');
});
