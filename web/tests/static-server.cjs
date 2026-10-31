const { createServer } = require('node:http');
const { readFileSync, statSync } = require('node:fs');
const { resolve, relative, extname, sep } = require('node:path');

async function serveStatic(directory, base = '/') {
  const root = resolve(directory);
  const server = createServer((request, response) => {
    try {
      const pathname = decodeURIComponent(new URL(request.url, 'http://127.0.0.1').pathname);
      if (!pathname.startsWith(base)) throw new Error('La ruta queda fuera del punto de montaje de pruebas');
      let file = resolve(root, pathname.slice(base.length) || 'index.html');
      const path = relative(root, file);
      if (path === '..' || path.startsWith(`..${sep}`)) throw new Error('La ruta queda fuera del directorio raíz de pruebas');
      if (statSync(file).isDirectory()) file = resolve(file, 'index.html');
      const mime = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript' }[extname(file)];
      if (!mime) throw new Error('El archivo no es un recurso web');
      response.writeHead(200, { 'Content-Type': `${mime}; charset=utf-8` });
      response.end(readFileSync(file));
    } catch {
      response.writeHead(404);
      response.end();
    }
  });
  await new Promise((resolve, reject) => {
    server.once('error', reject);
    server.listen(0, '127.0.0.1', resolve);
  });
  return {
    url: `http://127.0.0.1:${server.address().port}${base}`,
    close: () => new Promise(resolve => server.close(resolve)),
  };
}

module.exports = { serveStatic };
