// task 1746: CLS + ролики на vinyl-tm / portfolio / главной, 1440 и 390. node qa1746.mjs before|after
import { chromium } from 'playwright-core'
import { mkdirSync } from 'fs'
const tag = process.argv[2] || 'after'
const dir = `shots/np1746/live-${tag}`; mkdirSync(dir, { recursive: true })
const b = await chromium.launch({ channel: 'chrome' })
const pages = ['/portfolio/vinyl-tm/', '/portfolio/', '/']
for (const w of [1440, 390]) for (const path of pages) {
  const ctx = await b.newContext({ viewport: { width: w, height: 900 }, deviceScaleFactor: 1, isMobile: w < 500, hasTouch: w < 500 })
  const p = await ctx.newPage()
  await p.addInitScript(() => { window.__cls = 0; new PerformanceObserver(l => l.getEntries().forEach(e => { if (!e.hadRecentInput) window.__cls += e.value })).observe({ type: 'layout-shift', buffered: true }) })
  const r = await p.goto('https://ne-prosto.ru' + path + '?qa=' + Date.now(), { waitUntil: 'networkidle' })
  await p.waitForTimeout(2500)
  const cls = await p.evaluate(() => +window.__cls.toFixed(4))
  const info = { w, path, status: r.status(), cls, h1: await p.locator('h1').count(), hscroll: await p.evaluate(() => document.documentElement.scrollWidth > innerWidth) }
  if (tag === 'after') {
    const vids = []
    const n = await p.locator('.np-ss video').count()
    for (let i = 0; i < n; i++) {
      const v = p.locator('.np-ss video').nth(i)
      if (!(await v.isVisible())) continue
      await v.scrollIntoViewIfNeeded(); await p.waitForTimeout(2200)
      const st = await v.evaluate(e => ({ src: (e.currentSrc || '').replace(/^.*stageshow\//, ''), rs: e.readyState, paused: e.paused, t: +e.currentTime.toFixed(1), alt: e.dataset.ssAlt || '' }))
      vids.push(st)
      if (path.includes('vinyl')) await v.screenshot({ path: `${dir}/vinyl-${w}-v${i}.png` })
    }
    info.videos = vids
    await p.screenshot({ path: `${dir}/${path.replace(/\W+/g, '_') || 'home'}-${w}.png` })
  }
  console.log(JSON.stringify(info))
  await ctx.close()
}
await b.close()
