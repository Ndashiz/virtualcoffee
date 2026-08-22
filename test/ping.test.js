/* The café's only test, and the one part of it that can break in silence.
 *
 *     node test/ping.test.js
 *
 * It runs the REAL VCPing block straight out of index.html under stubbed globals, so every query
 * string it would put on the wire is asserted exactly — including the paths a browser cannot be
 * driven through: a genuinely visible tab, Do Not Track, an abandoned tab, a device armed as crew.
 *
 * Why this is worth having when nothing else here is tested: every failure mode of the ping is
 * INVISIBLE. The switch fails open, the counters fail quiet, and a browser blocks the response of
 * a broken cross-origin call without telling the page. Nothing on either side would ever report
 * that the café stopped counting — so the assertions have to stand in for the alarm.
 *
 * No dependencies, no runner, no package.json. Exit code 0 means green.
 */
const fs = require('fs');
const vm = require('vm');
const path = require('path');

// VC_INDEX points the suite at a different copy — a staged version, or a published one pulled
// back off the server — so "what is about to ship" can be checked, not just what is on disk.
const html = fs.readFileSync(process.env.VC_INDEX || path.join(__dirname, '..', 'index.html'), 'utf8');
const blocks = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map((m) => m[1]);
const source = blocks.find((b) => b.includes('window.VCPing'));
if (!source) throw new Error('VCPing block not found');

function run({ search = '', dnt = false, storage = {}, visible = true, hostname = 'ndashiz.be', protocol = 'https:' } = {}) {
  const sent = [];
  let now = 1_000_000;
  const intervals = [];
  const listeners = {};
  const store = { ...storage };
  let replaced = null;

  const doc = {
    get visibilityState() {
      return visible ? 'visible' : 'hidden';
    },
    referrer: '',
    addEventListener: (ev, fn) => ((listeners[ev] ??= []).push(fn)),
    createElement: () => ({ style: {}, setAttribute() {} }),
    body: { appendChild() {} },
    documentElement: { appendChild() {} },
  };

  const sandbox = {
    console,
    Date: new Proxy(Date, { get: (t, k) => (k === 'now' ? () => now : t[k]) }),
    setTimeout: () => 0,
    clearTimeout: () => {},
    setInterval: (fn) => (intervals.push(fn), intervals.length),
    Math,
    isFinite,
    RegExp,
    String,
    Uint8Array,
    decodeURIComponent,
    AbortController,
    URL,
    document: doc,
    navigator: dnt ? { doNotTrack: '1' } : {},
    history: { replaceState: (_a, _b, url) => (replaced = url) },
    location: { search, pathname: '/virtualcoffee/', hash: '', hostname, protocol },
    localStorage: {
      getItem: (k) => (k in store ? store[k] : null),
      setItem: (k, v) => (store[k] = String(v)),
      removeItem: (k) => delete store[k],
    },
    addEventListener: (ev, fn) => ((listeners[ev] ??= []).push(fn)),
    fetch: (url) => {
      sent.push(url.replace('https://jarvis.ndashiz.be/api/vc/ping?', '').replace('http://localhost:3011/api/vc/ping?', ''));
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ open: true }) });
    },
  };
  sandbox.window = sandbox;
  sandbox.crypto = undefined; // exercise the Math.random fallback: deterministic enough to assert shape
  vm.createContext(sandbox);
  vm.runInContext(source, sandbox);

  return {
    sent,
    store,
    replaced,
    ping: sandbox.VCPing,
    /** Advance the fake clock and fire every registered interval, like a browser would. */
    tick(seconds) {
      now += seconds * 1000;
      intervals.forEach((fn) => fn());
    },
    /**
     * Move the clock WITHOUT firing the intervals — the seconds that pass between two
     * heartbeats.
     *
     * The suite could not express "and then eight seconds later" before this existed, because
     * tick() couples the clock to the interval: any beat() called out of band saw a zero gap,
     * accrued nothing, and was swallowed by the `whole > sent` guard. Two assertions below
     * named a flush and in fact proved nothing — both flushes could be deleted from index.html
     * with the suite still green. Anything testing an on-demand flush must advance() first.
     */
    advance(seconds) {
      now += seconds * 1000;
    },
    poke() {
      (listeners.pointerdown || []).forEach((fn) => fn());
    },
    setVisible(v) {
      visible = v;
    },
    hide() {
      visible = false;
      (listeners.visibilitychange || []).forEach((fn) => fn());
    },
  };
}

let failures = 0;
function check(label, actual, expected) {
  const ok = JSON.stringify(actual) === JSON.stringify(expected);
  if (!ok) failures++;
  console.log(`${ok ? '  ok  ' : '  FAIL'} ${label}`);
  if (!ok) console.log(`        expected ${JSON.stringify(expected)}\n        actual   ${JSON.stringify(actual)}`);
}
/** Sessions are random, so assert against the query with the id masked out. */
const mask = (q) => q.replace(/s=[a-z0-9]{8}/, 's=<sid>');

console.log('\n— a plain visit —');
{
  const t = run();
  check('one load ping, no campaign, no crew', t.sent.map(mask), ['e=open&s=<sid>&l=en&r=direct']);
  check('session id is 8 lowercase alphanumerics', /^e=open&s=[a-z0-9]{8}&/.test(t.sent[0]), true);
}

console.log('\n— a shared LinkedIn link —');
{
  const t = run({ search: '?c=li-aug' });
  check('campaign rides every ping', t.sent.map(mask), ['e=open&s=<sid>&l=en&r=direct&c=li-aug']);
}
{
  const t = run({ search: '?utm_source=linkedin' });
  check('utm_source is accepted too', t.sent.map(mask), ['e=open&s=<sid>&l=en&r=direct&c=linkedin']);
}
{
  const t = run({ search: '?c=Li Aug 2026!!<script>' });
  check('a junk slug is normalised, never sent raw', t.sent.map(mask), ['e=open&s=<sid>&l=en&r=direct&c=liaug2026script']);
}
{
  const t = run({ search: '?c=' + '-'.repeat(20) });
  check('a slug that normalises to nothing is dropped', t.sent.map(mask), ['e=open&s=<sid>&l=en&r=direct']);
}

console.log('\n— arming one of Simon’s devices —');
{
  const t = run({ search: '?crew=doubleshot' });
  check('k=1 on the load ping', t.sent.map(mask), ['e=open&k=1&s=<sid>&l=en&r=direct']);
  check('the flag is persisted', t.store['vc:crew'], '1');
  check('the token is stripped from the address bar', t.replaced, '/virtualcoffee/');
}
{
  const t = run({ search: '?crew=doubleshot&c=li-aug' });
  check('a campaign beside it survives the strip', t.replaced, '/virtualcoffee/?c=li-aug');
}
{
  const t = run({ storage: { 'vc:crew': '1' } });
  check('an armed device stays armed with no parameter', t.sent.map(mask), ['e=open&k=1&s=<sid>&l=en&r=direct']);
}
{
  const t = run({ search: '?crew=off', storage: { 'vc:crew': '1' } });
  check('?crew=off disarms', t.sent.map(mask), ['e=open&s=<sid>&l=en&r=direct']);
  check('…and forgets the flag', t.store['vc:crew'], undefined);
}
{
  const t = run({ search: '?crew=wrong-token' });
  check('a wrong token arms nothing', t.sent.map(mask), ['e=open&s=<sid>&l=en&r=direct']);
}

console.log('\n— localhost is always crew —');
/* Local dev pings the REAL backend on purpose, and a cross-origin browser blocks the response but
   never the request: without this, every dev reload and every headless run lands in the public
   counters. It has already happened for real, which is why these assertions exist. */
for (const host of ['localhost', '127.0.0.1', '0.0.0.0', '[::1]']) {
  const t = run({ hostname: host });
  check(`${host} marks itself as crew`, t.sent.map(mask), ['e=open&k=1&s=<sid>&l=en&r=direct']);
}
{
  const t = run({ hostname: 'localhost', protocol: 'http:', search: '?crew=off' });
  check('…and ?crew=off cannot switch it back on', t.sent.map(mask), ['e=open&k=1&s=<sid>&l=en&r=direct']);
}
{
  const t = run({ hostname: '', protocol: 'file:' });
  check('a file:// copy is crew too', t.sent.map(mask), ['e=open&k=1&s=<sid>&l=en&r=direct']);
}
{
  const t = run({ hostname: 'ndashiz.be' });
  check('the real site is NOT crew', t.sent.map(mask), ['e=open&s=<sid>&l=en&r=direct']);
}
{
  // The obvious way to get this wrong: a substring test that also matches a real hostname.
  const t = run({ hostname: 'localhost.evil.example' });
  check('a hostname merely containing "localhost" is not crew', t.sent.map(mask), ['e=open&s=<sid>&l=en&r=direct']);
}

console.log('\n— Do Not Track —');
{
  const t = run({ dnt: true });
  t.ping.tap('enter');
  t.ping.tap('read', 'tv');
  t.tick(60);
  check('exactly one request, carrying nothing but the event', t.sent, ['e=open']);
}
{
  const t = run({ dnt: true, storage: { 'vc:crew': '1' } });
  check('Simon’s own phone still excludes itself under DNT', t.sent, ['e=open&k=1']);
}

console.log('\n— how long they stayed —');
{
  const t = run();
  t.tick(15);
  t.tick(15);
  check('cumulative seconds, not deltas', t.sent.map(mask).slice(1), [
    'e=hb&s=<sid>&l=en&r=direct&d=15',
    'e=hb&s=<sid>&l=en&r=direct&d=30',
  ]);
}
{
  const t = run({ visible: false });
  t.tick(15);
  t.tick(15);
  check('a background tab accrues nothing and sends nothing', t.sent.map(mask).slice(1), []);
}
{
  const t = run();
  t.tick(15); // counted: activity is fresh
  t.tick(200); // > 3 min with no sign of life → not counted
  t.poke();
  t.tick(15); // counted again
  check('an abandoned tab stops counting, and resumes on a sign of life', t.sent.map(mask).slice(1), [
    'e=hb&s=<sid>&l=en&r=direct&d=15',
    'e=hb&s=<sid>&l=en&r=direct&d=30',
  ]);
}
{
  const t = run();
  t.tick(15);
  t.ping.focus('press-sport');
  t.tick(15);
  t.advance(8);        /* eight seconds inside the current window, unseen by any heartbeat */
  t.ping.focus(null);  /* …and they belong to the newspaper, which is why focus() flushes first */
  check('closing a newspaper mid-window still books its seconds against it', t.sent.map(mask).slice(1), [
    'e=hb&s=<sid>&l=en&r=direct&d=15',
    'e=hb&s=<sid>&l=en&r=direct&i=press-sport&d=30',
    'e=hb&s=<sid>&l=en&r=direct&i=press-sport&d=38',
  ]);
}
{
  const t = run();
  t.tick(15);
  t.advance(9);  /* nine seconds no heartbeat has sent */
  t.hide();      /* going hidden is the last moment the page runs — they must not be lost */
  check('going hidden flushes the seconds no heartbeat has sent', t.sent.map(mask).slice(-1), [
    'e=hb&s=<sid>&l=en&r=direct&d=24',
  ]);
}

console.log('\n— the vocabulary —');
{
  const t = run();
  t.ping.tap('section', 'howibuilt');
  t.ping.tap('read', 'press-business');
  t.ping.tap('cvdl');
  t.ping.tap('linkedin');
  t.ping.tap('nonsense');
  t.ping.tap('read', 'nonsense-item');
  check('known events and items go, unknown ones never leave the page', t.sent.map(mask).slice(1), [
    'e=section&s=<sid>&l=en&r=direct&i=howibuilt',
    'e=read&s=<sid>&l=en&r=direct&i=press-business',
    'e=cvdl&s=<sid>&l=en&r=direct',
    'e=linkedin&s=<sid>&l=en&r=direct',
    'e=read&s=<sid>&l=en&r=direct',
  ]);
}

console.log(failures ? `\n${failures} FAILING\n` : '\nall green\n');
process.exit(failures ? 1 : 0);
