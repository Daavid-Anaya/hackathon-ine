const { test } = require('node:test');
const assert = require('node:assert/strict');
const { resolve } = require('node:path');
const { chromium } = require('playwright-core');
const { serveStatic } = require('./static-server.cjs');

const proposals = [
  ['E01', 'Flexibilidad en credencialización'],
  ['E02', 'Información y certidumbre logística'],
  ['E03', 'Cercanía territorial y comunitaria'],
  ['E04', 'Flujo en casillas y apoyo al funcionariado'],
  ['E05', 'Accesibilidad universal'],
];

async function openBase(t, options = {}) {
  const server = process.env.WEB_URL ? null : await serveStatic(resolve(__dirname, '../dist'));
  if (server) t.after(server.close);
  const entry = process.env.WEB_URL || server.url;
  const browser = await chromium.launch({ executablePath: process.env.WEB_BROWSER_PATH });
  t.after(() => browser.close());
  const context = await browser.newContext({ serviceWorkers: 'block', ...options });
  const remoteRequests = [];
  const errors = [];
  await context.route('**/*', route => {
    if (new URL(route.request().url()).origin === new URL(entry).origin) return route.continue();
    remoteRequests.push(route.request().url());
    return route.abort();
  });
  const page = await context.newPage();
  page.setDefaultTimeout(6000);
  page.on('pageerror', error => errors.push(error.message));
  page.on('console', message => {
    if (message.type() === 'error') errors.push(message.text());
  });
  t.after(() => {
    assert.deepEqual(errors, [], 'No debe haber errores de ejecución');
    assert.deepEqual(remoteRequests, [], 'La base no debe depender de servicios externos');
  });
  return { page, entry, context };
}

test('Base: inicio, catálogo, cinco páginas, evaluación y evidencia son navegables', async t => {
  const { page, entry } = await openBase(t, { reducedMotion: 'reduce' });
  await page.goto(entry);
  await page.getByRole('heading', { level: 1, name: 'De la evidencia a la acción institucional.' }).waitFor();
  const nav = page.getByRole('navigation', { name: 'Navegación principal' });
  assert.equal(await nav.getByRole('link').count(), 4);
  await page.getByRole('link', { name: 'Explorar las propuestas', exact: true }).click();
  await page.getByRole('heading', { level: 1, name: 'Cinco propuestas. Distintas formas de actuar.' }).waitFor();
  assert.equal(await nav.getByRole('link', { name: 'Propuestas', exact: true }).getAttribute('aria-current'), 'page');
  for (const [id, title] of proposals) {
    await page.getByRole('link', { name: new RegExp(`${id}.*${title}`) }).click();
    await page.getByRole('heading', { level: 1, name: title, exact: true }).waitFor();
    assert.ok(page.url().endsWith(`#/propuestas/${id}`));
    if (id === 'E01') await page.getByRole('heading', { name: 'Calculadora de cobertura TCHE', exact: true }).waitFor();
    else if (id === 'E02') await page.getByRole('combobox', { name: 'Casilla ficticia', exact: true }).waitFor();
    else if (id === 'E03') await page.getByRole('combobox', { name: 'Comunidad ficticia', exact: true }).waitFor();
    else if (id === 'E04') await page.getByRole('button', { name: 'Etapa 1: Orientación y acceso', exact: true }).waitFor();
    else await page.getByRole('heading', { name: 'Lista de verificación de accesibilidad', exact: true }).waitFor();
    assert.equal(await nav.getByRole('link', { name: 'Propuestas', exact: true }).getAttribute('aria-current'), 'page');
    await page.reload();
    await page.getByRole('heading', { level: 1, name: title, exact: true }).waitFor();
    await page.getByRole('link', { name: 'Volver al catálogo', exact: true }).click();
  }
  await nav.getByRole('link', { name: 'Evaluación', exact: true }).click();
  await page.getByRole('heading', { level: 1, name: 'Medir el servicio, no prometer votos.' }).waitFor();
  for (const indicator of ['TCHE', 'DRC', 'PACE', 'TAP', 'CEAF']) {
    await page.getByRole('heading', { name: new RegExp(indicator) }).waitFor();
  }
  await nav.getByRole('link', { name: 'Evidencia', exact: true }).click();
  await page.getByRole('heading', { level: 1, name: 'Lo que sabemos. Lo que falta comprobar.' }).waitFor();
  await page.goBack();
  await page.getByRole('heading', { level: 1, name: 'Medir el servicio, no prometer votos.' }).waitFor();
  await page.goForward();
  await page.getByRole('heading', { level: 1, name: 'Lo que sabemos. Lo que falta comprobar.' }).waitFor();
  assert.equal(await page.locator('h1').count(), 1);
  assert.equal(await page.evaluate(() => document.activeElement?.tagName), 'H1');
  assert.deepEqual(await page.evaluate(() => [localStorage.length, sessionStorage.length, document.cookie]), [0, 0, '']);
  await page.goto(`${entry}#/no-existe`);
  await page.getByRole('heading', { level: 1, name: 'Esta página no existe.' }).waitFor();
  await page.getByRole('link', { name: 'Volver al inicio', exact: true }).click();
  await page.getByRole('heading', { level: 1, name: 'De la evidencia a la acción institucional.' }).waitFor();
});

test('Base: navegación por teclado, diseño adaptable y paleta de las fichas', async t => {
  const { page, entry } = await openBase(t, { reducedMotion: 'reduce' });
  for (const width of [320, 768, 1440]) {
    await page.setViewportSize({ width, height: 900 });
    await page.goto(entry);
    await page.getByRole('heading', { level: 1 }).waitFor();
    await page.keyboard.press('Tab');
    assert.equal(await page.evaluate(() => document.activeElement?.textContent), 'Saltar al contenido');
    await page.keyboard.press('Enter');
    assert.equal(await page.evaluate(() => document.activeElement?.id), 'contenido');
    const nav = page.getByRole('navigation', { name: 'Navegación principal' });
    for (const label of ['Propuestas', 'Evaluación', 'Evidencia', 'Inicio']) {
      const link = nav.getByRole('link', { name: label, exact: true });
      await link.focus();
      assert.notEqual(await link.evaluate(el => getComputedStyle(el).outlineStyle), 'none');
      await page.keyboard.press('Enter');
      await page.getByRole('heading', { level: 1 }).waitFor();
      assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
      const box = await link.boundingBox();
      assert.ok(box.height >= 44 && box.width >= 44, `Destino táctil insuficiente: ${label}`);
    }
  }
  const palette = await page.evaluate(() => {
    const style = getComputedStyle(document.documentElement);
    return ['--purple', '--lavender', '--ink', '--heading'].map(token => style.getPropertyValue(token).trim().toLowerCase());
  });
  assert.deepEqual(palette, ['#674092', '#d1bdef', '#383b7e', '#49276f']);
});

test('Base: revelado al entrar en pantalla una sola vez, con alternativa de movimiento reducido', async t => {
  const { page, entry } = await openBase(t, { viewport: { width: 900, height: 600 } });
  await page.goto(`${entry}#/propuestas`);
  const lastCard = page.getByRole('link', { name: /E05.*Accesibilidad universal/ });
  await lastCard.waitFor();
  await lastCard.scrollIntoViewIfNeeded();
  await page.waitForFunction(() => document.querySelector('[data-proposal="E05"]')?.classList.contains('revealed'));
  assert.equal(await lastCard.evaluate(el => getComputedStyle(el).animationName), 'rise-in');
  await page.waitForFunction(() => document.querySelector('[data-proposal="E05"]')?.getAnimations().every(a => a.playState === 'finished'));
  await page.evaluate(() => scrollTo(0, 0));
  await lastCard.scrollIntoViewIfNeeded();
  assert.ok(await lastCard.evaluate(el => el.getAnimations().every(a => a.playState === 'finished')));
  await page.emulateMedia({ reducedMotion: 'reduce' });
  assert.equal(await lastCard.evaluate(el => getComputedStyle(el).animationName), 'none');
  assert.equal(await lastCard.evaluate(el => getComputedStyle(el).opacity), '1');
});

test('Base: el contenido permanece visible sin IntersectionObserver', async t => {
  const { page, entry, context } = await openBase(t);
  await context.addInitScript(() => { window.IntersectionObserver = undefined; });
  await page.goto(`${entry}#/propuestas`);
  const cards = page.getByRole('link', { name: /E0[1-5].*Ver propuesta/ });
  await cards.first().waitFor();
  assert.equal(await cards.count(), 5);
  for (const card of await cards.all()) assert.equal(await card.evaluate(el => getComputedStyle(el).opacity), '1');
});

test('Base: JavaScript desactivado muestra una explicación y no un espacio vacío', async t => {
  const { page, entry } = await openBase(t, { javaScriptEnabled: false });
  await page.goto(entry);
  await page.getByText('Activa JavaScript para explorar el demostrador.', { exact: true }).waitFor();
  await page.getByRole('link', { name: 'Consultar el portal del INE', exact: true }).waitFor();
});
