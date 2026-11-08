import { chromium } from 'playwright-core'
const [path, w] = [process.argv[2], +process.argv[3]]
const b = await chromium.launch({ channel: 'chrome' })
for (let k = 0; k < 3; k++) {
  const ctx = await b.newContext({ viewport: { width: w, height: 900 } }); const p = await ctx.newPage()
  await p.addInitScript(() => { window.__s = []; new PerformanceObserver(l => l.getEntries().forEach(e => { if (!e.hadRecentInput) window.__s.push([+e.value.toFixed(4), +e.startTime.toFixed(0), e.sources.map(s => (s.node && s.node.nodeType===1 ? s.node.tagName + '.' + (s.node.className||'').toString().slice(0,40) : s.node ? '#text' : '?') + ' ' + s.previousRect.y + '->' + s.currentRect.y).join(' | ')]) })).observe({ type: 'layout-shift', buffered: true }) })
  await p.goto('https://ne-prosto.ru' + path + '?c=' + Date.now(), { waitUntil: 'networkidle' }); await p.waitForTimeout(2500)
  console.log(k, JSON.stringify(await p.evaluate(() => window.__s)))
  await ctx.close()
}
await b.close()
