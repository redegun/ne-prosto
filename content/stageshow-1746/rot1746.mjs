import { chromium } from 'playwright-core'
const b = await chromium.launch({ channel: 'chrome' }); const p = await (await b.newContext({ viewport: { width: 1440, height: 900 } })).newPage()
await p.goto('https://ne-prosto.ru/portfolio/?r=' + Date.now(), { waitUntil: 'networkidle' })
const v = p.locator('video[data-ss-alt]').first(); await v.scrollIntoViewIfNeeded()
const seen = new Set()
for (let i = 0; i < 16; i++) { await p.waitForTimeout(2500); const s = await v.evaluate(e => e.currentSrc.replace(/^.*stageshow\//, '') + ' paused=' + e.paused); seen.add(s.split('/')[0]); console.log(s) }
console.log('distinct', [...seen]); await b.close()
