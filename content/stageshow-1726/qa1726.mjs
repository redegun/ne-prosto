import { chromium } from 'playwright-core'
const tag = process.argv[2] || 'after'
const pages = { portfolio: '/portfolio/', 'vinyl-tm': '/portfolio/vinyl-tm', kppf: '/portfolio/kppf', merci: '/portfolio/merci', home: '/' }
const b = await chromium.launch({ channel: 'chrome' })
for (const w of [1440, 390]) for (const [pg, path] of Object.entries(pages)) {
  const ctx = await b.newContext({ viewport: { width: w, height: 900 }, deviceScaleFactor: 1 })
  const p = await ctx.newPage()
  await p.addInitScript(() => { window.__cls = 0; new PerformanceObserver(l => l.getEntries().forEach(e => { if (!e.hadRecentInput) window.__cls += e.value })).observe({ type: 'layout-shift', buffered: true }) })
  const errs = []; p.on('pageerror', e => errs.push(e.message))
  const r = await p.goto('https://ne-prosto.ru' + path + '?qa=' + Date.now(), { waitUntil: 'networkidle', timeout: 60000 })
  const clsLoad = await p.evaluate(() => window.__cls)
  const sel = pg === 'portfolio' ? 'a[href*="merci"]' : pg === 'home' ? 'a.np-project__image[href*="vinyl"]' : '.np-ss, .process-wrapper'
  await p.locator(sel).first().scrollIntoViewIfNeeded()
  await p.waitForTimeout(3500)
  const st = await p.evaluate(() => [...document.querySelectorAll('.np-ss video')].filter(v => v.offsetParent).map(v => ({ paused: v.paused, t: +v.currentTime.toFixed(1), rs: v.readyState, src: (v.currentSrc || '').split('/').pop() })))
  const cls = await p.evaluate(() => window.__cls)
  const sw = await p.evaluate(() => [document.documentElement.scrollWidth, innerWidth])
  const h1 = await p.locator('h1').count()
  await p.screenshot({ path: `shots/np1726/${tag}-${pg}-${w}.png` })
  console.log(tag, w, pg, r.status(), 'h1', h1, 'CLSload', clsLoad.toFixed(4), 'CLS', cls.toFixed(4), 'sw', sw.join('/'), JSON.stringify(st), errs.join('|'))
  await ctx.close()
}
if (tag !== 'before') {
  const ctx = await b.newContext({ viewport: { width: 1440, height: 900 }, reducedMotion: 'reduce' })
  const p = await ctx.newPage(); await p.goto('https://ne-prosto.ru/portfolio/kppf', { waitUntil: 'networkidle' })
  console.log('reduced: videos', await p.locator('.np-ss video:visible').count(), 'imgs', await p.locator('.np-ss img').count())
}
await b.close()
