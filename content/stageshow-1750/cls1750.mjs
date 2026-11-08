// task 1750: CLS /portfolio/vinyl-tm 1440 и 390, N прогонов
import { chromium } from 'playwright-core'
const b = await chromium.launch({ channel: 'chrome' })
for (const w of [1440, 390]) { const out = []
  for (let k = 0; k < 5; k++) {
    const ctx = await b.newContext({ viewport: { width: w, height: 900 }, isMobile: w < 500, hasTouch: w < 500 })
    const p = await ctx.newPage()
    await p.addInitScript(() => { window.__cls = 0; window.__src = []; new PerformanceObserver(l => l.getEntries().forEach(e => { if (!e.hadRecentInput) { window.__cls += e.value; window.__src.push(e.sources.map(s => s.node ? (s.node.className || s.node.nodeName) : '?').join('|') + ':' + e.value.toFixed(3)) } })).observe({ type: 'layout-shift', buffered: true }) })
    await p.goto('https://ne-prosto.ru/portfolio/vinyl-tm/?c=' + Date.now(), { waitUntil: 'networkidle' }); await p.waitForTimeout(2500)
    out.push(await p.evaluate(() => [+window.__cls.toFixed(4), window.__src.slice(0, 3)])); await ctx.close() }
  console.log(w, JSON.stringify(out)) }
await b.close()
