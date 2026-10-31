const { test } = require('node:test');
const assert = require('node:assert/strict');
const { chromium } = require('playwright-core');

async function openConsultation(t) {
  assert.ok(process.env.WEB_URL, 'Ejecuta E02 desde el servicio de pruebas Docker');
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
  await page.goto(`${process.env.WEB_URL}#/propuestas/E02`);
  await page.getByRole('heading', { name: 'Consulta móvil guiada', exact: true }).waitFor();
  return {
    page,
    station: page.getByRole('combobox', { name: 'Casilla ficticia', exact: true }),
    status: page.getByRole('status', { name: 'Estado de afluencia simulado' }),
  };
}

test('E02: consulta tres fichas ficticias con ubicación, acceso, horario y accesibilidad', async t => {
  const { page, station, status } = await openConsultation(t);
  await page.getByText('Ejemplo sintético', { exact: true }).waitFor();
  assert.equal(await station.locator('option').count(), 3);
  const cases = [
    ['example-a', 'Centro comunitario de ejemplo', 'Sector A de la localidad ficticia.', 'Acceso a nivel de piso y pasillos amplios en el escenario.', 'Moderada'],
    ['example-b', 'Escuela de ejemplo', 'Sector B de la localidad ficticia.', 'Rampa por la entrada lateral en el escenario.', 'Baja'],
    ['example-c', 'Biblioteca de ejemplo', 'Sector C de la localidad ficticia.', 'Acceso con escalones; ruta accesible pendiente de verificar en el escenario.', 'Sin información'],
  ];
  for (const [value, heading, location, accessibility, crowd] of cases) {
    await station.selectOption(value);
    await page.getByRole('heading', { name: heading, exact: true }).waitFor();
    await page.getByText(location, { exact: true }).waitFor();
    await page.getByText(accessibility, { exact: true }).waitFor();
    await page.getByText('08:00–18:00 h · horario ilustrativo.', { exact: true }).waitFor();
    await status.getByText(crowd, { exact: true }).waitFor();
    assert.ok(await page.getByRole('definition').filter({ hasText: /Entrada|Acceso/ }).count() > 0);
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
  }
  assert.equal(await page.locator('iframe').count(), 0);
});

test('E02: cambia estados simulados de afluencia con teclado sin inventar tiempos de espera', async t => {
  const { page, station, status } = await openConsultation(t);
  const group = page.getByRole('group', { name: 'Simular afluencia' });
  for (const label of ['Baja', 'Moderada', 'Alta', 'Sin información']) {
    const radio = group.getByRole('radio', { name: label, exact: true });
    await radio.focus();
    assert.notEqual(await radio.evaluate(el => getComputedStyle(el).outlineStyle), 'none');
    await page.keyboard.press('Space');
    assert.equal(await radio.isChecked(), true);
    await status.getByText(label, { exact: true }).waitFor();
  }
  await status.getByText('No hay datos de afluencia en este escenario. No significa que la afluencia sea baja.', { exact: true }).waitFor();
  assert.equal(await status.getAttribute('aria-live'), 'polite');
  assert.equal(await status.getAttribute('aria-atomic'), 'true');
  await page.getByText('No son datos en tiempo real ni estimaciones de espera.', { exact: true }).waitFor();
  await station.selectOption('example-b');
  assert.equal(await group.getByRole('radio', { name: 'Baja', exact: true }).isChecked(), true);
  await status.getByText('Baja', { exact: true }).waitFor();
});

test('E02: descarta selección y afluencia al recargar o salir, sin guardar datos en la URL', async t => {
  const { page, station, status } = await openConsultation(t);
  const address = page.url();
  await station.selectOption('example-c');
  await page.getByRole('radio', { name: 'Alta', exact: true }).check();
  await status.getByText('Alta', { exact: true }).waitFor();
  assert.equal(page.url(), address);
  assert.deepEqual(await page.evaluate(() => [localStorage.length, sessionStorage.length, document.cookie]), [0, 0, '']);
  await page.reload();
  await status.getByText('Moderada', { exact: true }).waitFor();
  assert.equal(await station.inputValue(), 'example-a');
  await station.selectOption('example-b');
  await page.getByRole('link', { name: 'Volver al catálogo', exact: true }).click();
  await page.getByRole('link', { name: /E02.*Información y certidumbre logística/ }).click();
  assert.equal(await station.inputValue(), 'example-a');
  await status.getByText('Moderada', { exact: true }).waitFor();
});
