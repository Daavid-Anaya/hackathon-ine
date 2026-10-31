const { test } = require('node:test');
const assert = require('node:assert/strict');
const { chromium } = require('playwright-core');

async function openExplorer(t) {
  assert.ok(process.env.WEB_URL, 'Ejecuta E03 desde el servicio de pruebas Docker');
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
  await page.goto(`${process.env.WEB_URL}#/propuestas/E03`);
  await page.getByRole('heading', { name: 'Explorador territorial', exact: true }).waitFor();
  return {
    page,
    community: page.getByRole('combobox', { name: 'Comunidad ficticia', exact: true }),
    barriers: page.getByRole('group', { name: 'Barreras del escenario' }),
    summary: page.getByRole('status', { name: 'Resumen de medidas' }),
  };
}

const choices = [
  ['Traslado y dispersión', 'Evaluar cercanía territorial'],
  ['Espera con acompañantes', 'Preparar una espera segura y sombreada'],
  ['Información oral o bilingüe', 'Adaptar los canales de información'],
];

test('E03: explora comunidades ficticias y las medidas, recursos y condiciones de cada barrera', async t => {
  const { page, community, summary } = await openExplorer(t);
  await page.getByText('Ejemplo sintético', { exact: true }).waitFor();
  assert.equal(await community.locator('option').count(), 3);
  const expectedDetails = [
    [/Recorridos de campo/, /acceso abierto/, /Consejo Distrital/],
    [/Mobiliario, sombra/, /comunitaria abierta/, /seguridad/],
    [/Personal bilingüe/, /Radio comunitaria/, /revisión institucional/],
  ];
  for (const [index, [barrier, title]] of choices.entries()) {
    await community.selectOption(`community-${index + 1}`);
    await page.getByRole('heading', { name: `Comunidad ficticia ${String.fromCharCode(65 + index)}`, exact: true }).waitFor();
    assert.equal(await page.getByRole('checkbox', { name: barrier, exact: true }).isChecked(), true);
    const option = page.getByRole('article', { name: title, exact: true });
    await option.waitFor();
    await option.getByText('Recursos necesarios', { exact: true }).waitFor();
    await option.getByText('Canales de acceso voluntario', { exact: true }).waitFor();
    await option.getByText('Condiciones y validación', { exact: true }).waitFor();
    const details = await option.getByRole('definition').allTextContents();
    assert.equal(details.length, 3);
    for (const [field, expected] of expectedDetails[index].entries()) assert.match(details[field], expected);
    assert.equal(await summary.textContent(), '1 opción para estudiar.');
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
  }
  await page.getByText('Ninguna selección aprueba la instalación de casillas ni sustituye un dictamen técnico.', { exact: true }).waitFor();
});

test('E03: combina barreras por teclado y distingue ausencia de selección de ausencia de necesidades', async t => {
  const { page, community, barriers, summary } = await openExplorer(t);
  await community.selectOption('community-1');
  for (const [label] of choices) {
    const checkbox = barriers.getByRole('checkbox', { name: label, exact: true });
    if (await checkbox.isChecked()) await checkbox.uncheck();
  }
  assert.equal(await summary.textContent(), '0 opciones para estudiar.');
  await page.getByRole('heading', { name: 'Sin barreras seleccionadas', exact: true }).waitFor();
  await page.getByText('Esto no demuestra que no existan barreras. Hace falta un diagnóstico territorial independiente.', { exact: true }).waitFor();
  await community.focus();
  for (const [label, title] of choices) {
    const checkbox = barriers.getByRole('checkbox', { name: label, exact: true });
    await page.keyboard.press('Tab');
    assert.equal(await checkbox.evaluate(el => document.activeElement === el), true);
    assert.notEqual(await checkbox.evaluate(el => getComputedStyle(el).outlineStyle), 'none');
    await page.keyboard.press('Space');
    assert.equal(await checkbox.isChecked(), true);
    await page.getByRole('article', { name: title, exact: true }).waitFor();
  }
  assert.equal(await summary.textContent(), '3 opciones para estudiar.');
  assert.equal(await summary.getAttribute('aria-live'), 'polite');
  assert.equal(await summary.getAttribute('aria-atomic'), 'true');
  assert.equal(await page.getByRole('article').count(), 3);
});

test('E03: restablece escenario y barreras al recargar o salir, sin guardar selección', async t => {
  const { page, community, barriers, summary } = await openExplorer(t);
  const address = page.url();
  await community.selectOption('community-3');
  await barriers.getByRole('checkbox', { name: 'Traslado y dispersión', exact: true }).check();
  assert.equal(await summary.textContent(), '2 opciones para estudiar.');
  assert.equal(page.url(), address);
  assert.deepEqual(await page.evaluate(() => [localStorage.length, sessionStorage.length, document.cookie]), [0, 0, '']);
  await page.reload();
  await community.waitFor();
  assert.equal(await community.inputValue(), 'community-1');
  assert.equal(await barriers.getByRole('checkbox', { name: 'Información oral o bilingüe', exact: true }).isChecked(), false);
  await community.selectOption('community-2');
  await page.getByRole('link', { name: 'Volver al catálogo', exact: true }).click();
  await page.getByRole('link', { name: /E03.*Cercanía territorial y comunitaria/ }).click();
  assert.equal(await community.inputValue(), 'community-1');
  assert.equal(await summary.textContent(), '1 opción para estudiar.');
});
