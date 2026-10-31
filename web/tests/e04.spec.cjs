const { test } = require('node:test');
const assert = require('node:assert/strict');
const { chromium } = require('playwright-core');

const stages = [
  ['Orientación y acceso', /Señalización/, /Capacitación modular/],
  ['Mesa de atención', /Mobiliario/, /Iluminación/],
  ['Espacio de votación', /cancel portátil de accesibilidad/, /uso de materiales/],
  ['Urnas y salida', /hacia las urnas/, /acompañamiento de CAE/],
];

async function openFlow(t) {
  assert.ok(process.env.WEB_URL, 'Ejecuta E04 desde el servicio de pruebas Docker');
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
  await page.goto(`${process.env.WEB_URL}#/propuestas/E04`);
  await page.getByRole('heading', { name: 'Recorrido visual interactivo', exact: true }).waitFor();
  return {
    page,
    flow: page.getByRole('list', { name: 'Etapas del recorrido' }),
    summary: page.getByRole('status', { name: 'Etapa seleccionada' }),
  };
}

test('E04: explora cuatro etapas con distribución ilustrativa y apoyos al funcionariado', async t => {
  const { page, flow, summary } = await openFlow(t);
  await page.getByText('Esquema ilustrativo', { exact: true }).waitFor();
  assert.equal(await flow.getByRole('button').count(), 4);
  for (const [index, [title, layout, support]] of stages.entries()) {
    const button = flow.getByRole('button', { name: `Etapa ${index + 1}: ${title}`, exact: true });
    await button.click();
    const detail = page.getByRole('region', { name: title, exact: true });
    await detail.waitFor();
    assert.equal(await button.getAttribute('aria-controls'), 'e04-stage-detail');
    assert.equal(await button.getAttribute('aria-pressed'), 'true');
    assert.equal(await flow.getByRole('button', { pressed: true }).count(), 1);
    const definitions = await detail.getByRole('definition').allTextContents();
    assert.equal(definitions.length, 2);
    assert.match(definitions[0], layout);
    assert.match(definitions[1], support);
    assert.equal(await summary.textContent(), `Etapa ${index + 1} de 4: ${title}.`);
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
  }
  await page.getByText('Este esquema no mide filas ni estima tiempos de espera.', { exact: true }).waitFor();
  await page.getByText('No es un plano real ni un protocolo electoral oficial.', { exact: true }).waitFor();
});

test('E04: permite recorrer las etapas con Tab y Space y anuncia la selección', async t => {
  const { page, flow, summary } = await openFlow(t);
  const first = flow.getByRole('button', { name: 'Etapa 1: Orientación y acceso', exact: true });
  let reached = false;
  for (let n = 0; n < 16; n++) {
    await page.keyboard.press('Tab');
    if (await first.evaluate(el => el === document.activeElement)) { reached = true; break; }
  }
  assert.ok(reached, 'La primera etapa debe ser alcanzable desde el inicio del documento');
  for (const [index, [title]] of stages.entries()) {
    if (index) await page.keyboard.press('Tab');
    const button = flow.getByRole('button', { name: `Etapa ${index + 1}: ${title}`, exact: true });
    assert.equal(await button.evaluate(el => el === document.activeElement), true);
    assert.notEqual(await button.evaluate(el => getComputedStyle(el).outlineStyle), 'none');
    await page.keyboard.press('Space');
    await page.getByRole('region', { name: title, exact: true }).waitFor();
  }
  assert.equal(await summary.getAttribute('aria-live'), 'polite');
  assert.equal(await summary.getAttribute('aria-atomic'), 'true');
});

test('E04: restablece la etapa inicial al recargar o salir sin guardar datos', async t => {
  const { page, flow, summary } = await openFlow(t);
  const address = page.url();
  await flow.getByRole('button', { name: 'Etapa 4: Urnas y salida', exact: true }).click();
  assert.equal(page.url(), address);
  assert.deepEqual(await page.evaluate(() => [localStorage.length, sessionStorage.length, document.cookie]), [0, 0, '']);
  await page.reload();
  await summary.waitFor();
  assert.equal(await summary.textContent(), 'Etapa 1 de 4: Orientación y acceso.');
  await flow.getByRole('button', { name: 'Etapa 3: Espacio de votación', exact: true }).click();
  await page.getByRole('link', { name: 'Volver al catálogo', exact: true }).click();
  await page.getByRole('link', { name: /E04.*Flujo en casillas y apoyo al funcionariado/ }).click();
  assert.equal(await summary.textContent(), 'Etapa 1 de 4: Orientación y acceso.');
});
