import { chromium } from 'playwright-core'
const b = await chromium.launch({ channel: 'chrome' })
for (const w of [1440, 390]) {
  const ctx = await b.newContext({ viewport: { width: w, height: 900 }, isMobile: w < 500 })
  const p = await ctx.newPage(); await p.goto('https://ne-prosto.ru/portfolio/vinyl-tm/?s=' + Date.now(), { waitUntil: 'networkidle' })
  const plq = p.locator('text=×1000').first(); await plq.scrollIntoViewIfNeeded(); await p.waitForTimeout(800)
  await p.screenshot({ path: `shots/np1750/live-after/plaque-${w}.png` })
  const h = p.locator('h2', { hasText: 'Органика по Метрике' }); await h.scrollIntoViewIfNeeded(); await p.evaluate(() => scrollBy(0, -40)); await p.waitForTimeout(3000)
  await p.screenshot({ path: `shots/np1750/live-after/organika-${w}.png` }); await ctx.close() }
await b.close()
