// CI gate: extract the inline <script> from public/index.html and syntax-check it.
// Catches the class of bug where one bad template literal kills the whole page
// (server + API stay 200, but the app sits at "Loading…" forever).
const fs = require('fs');
const vm = require('vm');

const html = fs.readFileSync('public/index.html', 'utf-8');
const m = html.match(/<script>([\s\S]*?)<\/script>/);
if (!m) { console.error('FAIL: no inline <script> found in public/index.html'); process.exit(1); }
try {
  new vm.Script(m[1], { filename: 'public/index.html <inline script>' });
  console.log('OK: inline frontend JS compiles (' + m[1].length + ' chars)');
} catch (e) {
  console.error('FAIL: inline frontend JS has a syntax error — the page would be stuck at "Loading…":');
  console.error(e.stack.split('\n').slice(0, 6).join('\n'));
  process.exit(1);
}
