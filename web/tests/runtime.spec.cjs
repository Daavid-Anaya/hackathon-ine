const { test } = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { resolve } = require('node:path');

test('Las dependencias directas están fijadas y coinciden con el bloqueo instalado', () => {
  const root = resolve(__dirname, '..');
  const manifest = JSON.parse(readFileSync(resolve(root, 'package.json'), 'utf8'));
  const lock = JSON.parse(readFileSync(resolve(root, 'package-lock.json'), 'utf8'));
  for (const kind of ['dependencies', 'devDependencies']) {
    for (const [name, version] of Object.entries(manifest[kind])) {
      assert.match(version, /^\d+\.\d+\.\d+$/);
      assert.equal(lock.packages[''][kind][name], version);
      assert.equal(lock.packages[`node_modules/${name}`].version, version);
      const installed = JSON.parse(readFileSync(resolve(root, 'node_modules', name, 'package.json'), 'utf8'));
      assert.equal(installed.version, version);
    }
  }
  assert.ok(!Object.keys(lock.packages).some(path => /astro/i.test(path)));
  const config = JSON.parse(readFileSync(resolve(root, 'tsconfig.json'), 'utf8'));
  assert.equal(config.compilerOptions.strict, true);
});

test('Docker sirve solo la compilación estática, sin fuentes ni archivos internos del proyecto', async () => {
  assert.ok(process.env.WEB_URL, 'Ejecuta las comprobaciones de la web mediante Docker Compose');
  const base = new URL(process.env.WEB_URL);
  const response = await fetch(base);
  assert.equal(response.status, 200);
  assert.match(response.headers.get('content-type'), /text\/html/);
  assert.match(response.headers.get('server'), /nginx/i);
  const html = await response.text();
  assert.equal(html, readFileSync(resolve(__dirname, '../dist/index.html'), 'utf8'));
  for (const path of ['package.json', 'package-lock.json', 'src/data/profiles.js', 'src/app/App.tsx',
    'vite.config.ts', 'tsconfig.json', 'README.md',
    '.git/config', 'data/sources.json', 'outputs/', 'docs/documento-tecnico.pdf', 'unknown-route']) {
    const result = await fetch(new URL(path, base));
    assert.equal(result.status, 404, `Ruta accesible de forma inesperada: ${path}`);
    assert.equal(await (await fetch(base)).text(), html, 'Las solicitudes rechazadas no deben alterar la web');
  }
  const write = await fetch(new URL('index.html', base), { method: 'PUT', body: 'entrada-de-prueba-rechazada' });
  assert.equal(write.status, 405);
  assert.equal(await (await fetch(base)).text(), html, 'Una escritura rechazada no debe alterar la web');
  for (const [, asset] of html.matchAll(/(?:src|href)="([^"]+\.css)"/g)) {
    const result = await fetch(new URL(asset, base));
    assert.equal(result.status, 200);
    assert.match(result.headers.get('content-type'), /text\/css/);
  }
});
