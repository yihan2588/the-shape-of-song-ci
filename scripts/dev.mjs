import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { resolve, extname } from 'node:path';
import atlas from '../api/atlas.js';
import neighbors from '../api/neighbors.js';

const publicDir = fileURLToPath(new URL('../public/', import.meta.url));
const types = { '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.json': 'application/json' };
const server = createServer(async (req, res) => {
  res.status = code => { res.statusCode = code; return res; };
  res.json = data => { res.setHeader('Content-Type', 'application/json; charset=utf-8'); res.end(JSON.stringify(data)); };
  const url = new URL(req.url, 'http://localhost');
  req.query = Object.fromEntries(url.searchParams);
  if (url.pathname === '/api/atlas') return atlas(req, res);
  if (url.pathname === '/api/neighbors') return neighbors(req, res);
  try {
    const path = resolve(publicDir, '.' + (url.pathname === '/' ? '/index.html' : decodeURIComponent(url.pathname)));
    if (!path.startsWith(publicDir)) throw new Error('Not found');
    res.setHeader('Content-Type', types[extname(path)] || 'application/octet-stream');
    res.end(await readFile(path));
  } catch {
    res.statusCode = 404; res.end('Not found');
  }
});
server.listen(Number(process.env.PORT || 3210), '127.0.0.1', () => console.log(`The shape of Song Ci: http://127.0.0.1:${server.address().port}`));
