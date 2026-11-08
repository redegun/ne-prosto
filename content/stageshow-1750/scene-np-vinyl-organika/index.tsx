import { BarChart3 } from 'lucide-react'
import { Chart, chartPoints, Phone, Stage, type Act } from '../../kit'
import '../np-fonts/fonts.css'
import '../np-vinyl/vinyl.css'
import '../np-vinyl-marki/vx.css'
import './organika.css'
import logo from '../np-vinyl/logo.svg'

// Портфолио «Непросто», кейс Vinyl-TM (#1750): органика по Метрике.
// Данные: Яндекс Метрика, счётчик 26883291, визиты из поисковых систем
// (последний значимый источник) по месяцам, 01.2022–10.2026 (раньше 2022 API данных не отдаёт).
// Только индекс: средний месяц 2022 = 1, ось Y без значений. Файл: deploy1750/organika-index.json.

type S = { src: boolean; line: boolean; pins: number; years: boolean }
const initial: S = { src: false, line: false, pins: 0, years: false }
const POSTER: S = { src: true, line: true, pins: 3, years: true }

// индекс по месяцам, 2022-01 … 2026-10 (2022 = 1)
const IDX = [0.83, 0.85, 0.99, 1.11, 1.17, 1.09, 1.1, 1.13, 0.94, 0.95, 0.94, 0.9, 1.02, 0.97, 1.3, 1.48, 1.37, 1.28, 1.3, 1.83, 1.89, 1.74, 1.71, 1.5, 1.62, 1.81, 2.2, 2.36, 2.38, 2.08, 2.06, 2.12, 2.12, 1.95, 1.64, 1.39, 1.68, 1.75, 2.19, 2.15, 2.01, 1.73, 1.69, 1.64, 1.49, 1.4, 1.25, 1.07, 1.18, 1.26, 1.8, 1.86, 1.9, 2.08, 2.04, 2.08, 2.04, 2.22]
// среднее по годам (2026 — январь–октябрь)
const YEARS: [string, number, string][] = [['2022', 1, '1'], ['2023', 1.45, '1,45'], ['2024', 1.98, '1,98'], ['2025', 1.67, '1,67'], ['2026', 1.85, '1,85']]
const MAX = 2.75
const PINS: [number, string][] = [[0, '2022 = 1'], [28, '×2,4 · май 2024'], [57, '×2,2 · окт 2026']]

async function script(a: Act<S>) {
  await a.wait(700)
  await a.move({ at: 'src', x: 0.5, y: 0.6 })
  await a.wait(120)
  a.mark('src')
  await a.click()
  await a.set({ src: true, line: true })
  await a.wait(1300)
  a.mark('pins')
  await a.set({ pins: 1 })
  await a.wait(450)
  await a.set({ pins: 2 })
  await a.wait(450)
  await a.set({ pins: 3, years: true })
  await a.move('rest')
  await a.wait(3400)
  a.mark('reset')
  await a.set({ years: false, pins: 0 })
  await a.wait(350)
  await a.set({ line: false, src: false })
  await a.move(a.layout === 'compact' ? { x: 250, y: 120 } : { x: 330, y: 150 })
  await a.wait(1500)
}

function Swap2({ on, a, b }: { on: boolean; a: string; b: string }) {
  return (
    <span className="np-swap">
      <span data-on={!on || undefined}>{a}</span>
      <span data-on={on || undefined}>{b}</span>
    </span>
  )
}

function Plot({ s, w, h }: { s: S; w: number; h: number }) {
  const pts = chartPoints({ data: IDX, width: w, height: h, max: MAX })
  return (
    <div className="og-plot" style={{ width: w, height: h + 22 }}>
      {[0.25, 0.5, 0.75].map((f) => (
        <span key={f} className="og-grid" style={{ top: Math.round(h * f) }} />
      ))}
      <Chart data={IDX} width={w} height={h} show={s.line} max={MAX} className="vt-chart" />
      {PINS.map(([i, t], k) => {
        const p = pts[i]
        const side = i === 0 ? 'l' : i === IDX.length - 1 ? 'r' : 'c'
        return (
          <span key={i} className="og-pin" data-side={side} data-on={s.pins > k || undefined} style={{ left: p.x, top: p.y }}>
            <i />
            <b>{t}</b>
          </span>
        )
      })}
      {['2022', '2023', '2024', '2025', '2026'].map((y, k) => (
        <span key={y} className="og-year" data-first={k === 0 || undefined} style={{ top: h + 6, left: pts[k * 12].x }}>
          {y}
        </span>
      ))}
    </div>
  )
}

export default function NpVinylOrganika() {
  return (
    <Stage<S>
      width={720}
      height={540}
      compact={{ below: 600, width: 358, height: 560 }}
      initial={initial}
      poster={POSTER}
      script={script}
      cursor={{ at: { wide: { x: 330, y: 150 }, compact: { x: 250, y: 120 } } }}
      className="vt"
    >
      {(s, _r, layout) => {
        const compact = layout === 'compact'
        const report = (
          <div className="vt-page og-page">
            <div className="og-top">
              <BarChart3 size={18} strokeWidth={2.2} />
              <b>Источники трафика</b>
              <span className="og-site">vinyl-tm.ru</span>
            </div>
            <div className="og-body">
              <div className="og-chips">
                <span className="vx-pill">Все визиты</span>
                <span className="vx-pill" data-target="src" data-on={s.src || undefined}>
                  Поисковые системы
                </span>
                {!compact && <span className="vx-pill">Реклама</span>}
              </div>
              <div className="og-card">
                <div className="og-card__h">
                  <span>Визиты из поиска по месяцам</span>
                  <em>индекс, 2022 = 1</em>
                </div>
                <Plot s={s} w={compact ? 270 : 390} h={compact ? 150 : 190} />
              </div>
              <div className="og-note">Среднее по году к 2022</div>
              <div className="og-yrs">
                {YEARS.map(([y, , t]) => (
                  <span key={y} className="og-yr" data-on={s.years || undefined}>
                    <i>{y}</i>
                    <b>{t}</b>
                  </span>
                ))}
              </div>
              <div className="og-more" />
            </div>
            <span className="vt-rest" data-target="rest" />
          </div>
        )
        return compact ? (
          <>
            <div className="vt-win vt-win--c ss-window">{report}</div>
            <div className="vx-sat" data-on={s.years || undefined}>
              <span className="vx-sat__l">Октябрь 2026 к 2022 году</span>
              <span className="vx-sat__n">
                <Swap2 on={s.years} a="×1" b="×2,2" />
              </span>
            </div>
          </>
        ) : (
          <>
            <div className="vt-win og-win ss-window">
              <div className="vt-bar">
                <span />
                <span />
                <span />
                <em>metrika.yandex.ru · vinyl-tm.ru</em>
              </div>
              {report}
            </div>
            <Phone width={200} frame="pro" className="vt-phone">
              <div className="vt-ph">
                <img src={logo} alt="" className="vt-ph__logo" />
                <div className="vt-seo" data-on={s.years || undefined}>
                  <span className="vx-ph-k">Органика к 2022</span>
                  <span className="vx-ph-n">
                    <Swap2 on={s.years} a="×1" b="×2,2" />
                  </span>
                  <Chart data={YEARS.map((y) => y[1])} kind="bars" width={290} height={150} show={s.years} max={2.2} className="vt-chart" />
                  <span className="vt-seo__y og-ph-y">
                    {YEARS.map(([y]) => (
                      <span key={y}>{y.slice(2)}</span>
                    ))}
                  </span>
                </div>
                <div className="vt-ph__row">
                  <span className="vt-ph__k">Источник</span>
                  <b>Метрика</b>
                </div>
              </div>
            </Phone>
          </>
        )
      }}
    </Stage>
  )
}
