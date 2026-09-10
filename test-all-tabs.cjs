// Smoke test: click through EVERY nav tab of the LIVE page against the LIVE API.
// A view whose fetch hangs or throws = a tab stuck at Loading/Error.
// Usage: node test-all-tabs.cjs [comma,separated,tabs]   (default: all 10)
const { JSDOM } = require('jsdom');

const BASE = process.env.SMOKE_URL || 'https://racgp-study.limkangxian99.workers.dev';
const TABS = (process.argv[2] || 'today,dashboard,curriculum,questions,cce,guidelines,resources,rapid,schedule,mistakes,meta').split(',');
const sleep = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  const html = await (await fetch(BASE + '/')).text();
  const stripped = html.replace(/<script>[\s\S]*?<\/script>/, '<script id="appjs"></script>');
  const dom = new JSDOM(stripped, { url: BASE + '/', runScripts: 'outside-only', pretendToBeVisual: true });
  const { window } = dom;

  window.fetch = (input, opts) => {
    const url = new URL(String(input), BASE).href;
    const t0 = Date.now();
    return fetch(url, opts).then(r => {
      console.log(`  fetch ${url.replace(BASE, '')} -> ${r.status} in ${Date.now() - t0}ms`);
      if (!r.ok) throw new Error('HTTP ' + r.status + ' ' + url);
      return r;
    });
  };

  const errors = [];
  window.addEventListener('error', e => errors.push(e.message));
  window.console.error = (...a) => { errors.push(a.map(String).join(' ')); };

  // run the page's actual inline script
  window.eval(html.match(/<script>([\s\S]*?)<\/script>/)[1]);

  await sleep(1500); // let initial dashboard render settle
  const results = [];
  for (const tab of TABS) {
    // buttons are in NAV order; map tab id -> index (labels contain emojis: 'meta' renders as 'Exam Map')
    const NAV_IDS = ['today','dashboard','curriculum','questions','cce','guidelines','resources','rapid','schedule','mistakes','meta'];
    const idx = NAV_IDS.indexOf(tab);
    const btn = idx >= 0 ? [...window.document.querySelectorAll('nav button')][idx] : null;
    if (!btn) { results.push([tab, 'NO BUTTON']); continue; }
    btn.onclick();  // triggers render() for that tab
    await sleep(2500); // let async fetches + innerHTML settle
    const app = window.document.getElementById('app');
    const txt = (app.textContent || '').trim();
    if (txt.startsWith('Loading') || txt.includes('Loading…')) results.push([tab, 'STUCK AT LOADING']);
    else if (txt.includes('⚠️ Error')) results.push([tab, 'ERROR BOX: ' + txt.slice(0, 160)]);
    else if (txt.length < 10) results.push([tab, 'EMPTY: ' + JSON.stringify(txt.slice(0, 80))]);
    else results.push([tab, `OK (${txt.length} chars: "${txt.slice(0, 60).replace(/\s+/g, ' ')}…")`]);
  }
  console.log('\n===== TAB RESULTS =====');
  results.forEach(([t, r]) => console.log(`${t.padEnd(12)} ${r}`));
  const bad = results.filter(([, r]) => !r.startsWith('OK'));
  console.log(bad.length ? `\nFAILING TABS: ${bad.map(([t]) => t).join(', ')}` : '\nALL TABS OK');
  if (errors.length) { console.log('\nPage errors:'); errors.slice(0, 10).forEach(e => console.log('  ' + e)); }
  process.exit(bad.length ? 1 : 0);
})().catch(e => { console.error('HARNESS ERROR:', e.message); process.exit(2); });
