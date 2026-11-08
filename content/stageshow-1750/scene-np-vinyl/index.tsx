import { Calculator, Megaphone, Phone as PhoneIcon, Shield } from 'lucide-react'
import { Chart, Collapse, Count, Phone, Stage, type Act } from '../../kit'
import '../np-fonts/fonts.css'
import './vinyl.css'
import logo from './logo.svg'

// Портфолио «Непросто», кейс Vinyl-TM: калькулятор стоимости оклейки на сайте
// клиента (шаги и подписи — с vinyl-tm.ru/services/okleyka-auto/kalkulyator)
// + телефон-сателлит: рост визитов из поиска с 2019 года ×1000 (только относительные цифры, #1750).
// Цена расчёта — иллюстрация. Стиль — живой vinyl-tm.ru: Lato, #192632, #e01860.

type S = { kind: boolean; car: number; area: number; price: boolean; sent: boolean; seo: boolean }
const initial: S = { kind: false, car: -1, area: 10, price: false, sent: false, seo: false }
const POSTER: S = { kind: true, car: 1, area: 18, price: true, sent: false, seo: true }

const CARS = [{ name: 'Легковой' }, { name: 'Газель' }, { name: 'Фургон' }, { name: 'Автобус' }]
const VISITS = [2, 3, 5, 8, 12, 18, 26, 35, 47, 60, 78, 100]

async function script(a: Act<S>) {
  await a.wait(1100)
  await a.move({ at: 'kind', x: 0.42, y: 0.62 })
  await a.wait(120)
  a.mark('kind')
  await a.click()
  await a.set({ kind: true })
  await a.wait(450)
  await a.move({ at: 'car-1', x: 0.55, y: 0.7 })
  await a.wait(100)
  a.mark('car')
  await a.click()
  await a.set({ car: 1 })
  await a.wait(200)
  a.mark('area')
  await a.set({ area: 18 })
  await a.wait(700)
  await a.set({ price: true, seo: true })
  await a.move({ at: 'send', x: 0.9, y: 0.75 })
  await a.wait(500)
  a.mark('send')
  await a.click()
  await a.set({ sent: true })
  await a.move('rest')
  await a.wait(3000)
  a.mark('reset')
  await a.set({ sent: false, price: false, seo: false })
  await a.wait(300)
  await a.set({ area: 10, car: -1 })
  await a.wait(300)
  await a.set({ kind: false })
  await a.move(a.layout === 'compact' ? { x: 250, y: 120 } : { x: 330, y: 150 })
  await a.wait(500)
}

// Two labels in one cell, crossfaded: the button never changes width
function Swap2({ on, a, b }: { on: boolean; a: string; b: string }) {
  return (
    <span className="np-swap">
      <span data-on={!on || undefined}>{a}</span>
      <span data-on={on || undefined}>{b}</span>
    </span>
  )
}

export default function NpVinyl() {
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
        const page = (
          <div className="vt-page">
            <header className="vt-head">
              <img src={logo} alt="" className="vt-logo" />
              <span className="vt-tel">8 (800) 333-60-59</span>
              <span className="vt-call">
                <PhoneIcon size={12} strokeWidth={2.4} />
                Заказать звонок
              </span>
            </header>
            <div className="vt-body">
              <h3 className="vt-h1">
                <Calculator size={18} strokeWidth={2.2} />
                Калькулятор стоимости оклейки
              </h3>
              <div className="vt-step">Шаг 1. Тип услуги</div>
              <div className="vt-kinds">
                <div className="vt-kind" data-target="kind" data-on={s.kind || undefined}>
                  <Megaphone size={18} strokeWidth={2} />
                  <span className="vt-kind__t">
                    <b>Брендирование</b>
                    <i>Рекламная плёнка с печатью</i>
                  </span>
                  <span className="vt-radio" />
                </div>
                <div className="vt-kind">
                  <Shield size={18} strokeWidth={2} />
                  <span className="vt-kind__t">
                    <b>Защитная плёнка</b>
                    <i>PPF от сколов</i>
                  </span>
                  <span className="vt-radio" />
                </div>
              </div>
              <Collapse open={s.kind} reveal="drop">
                <div className="vt-step">Шаг 2. Транспорт и площадь</div>
                <div className="vt-cars">
                  {CARS.map((c, i) => (
                    <span key={c.name} className="vt-car" data-target={`car-${i}`} data-on={s.car === i || undefined}>
                      {c.name}
                    </span>
                  ))}
                </div>
                <div className="vt-area">
                  <span>Площадь, м²</span>
                  <span className="vt-track">
                    <span className="vt-fill" style={{ transform: `scaleX(${s.area / 24})` }} />
                  </span>
                  <b>
                    <Count value={s.area} duration={600} />
                  </b>
                </div>
              </Collapse>
              <Collapse open={s.price} reveal="drop">
                <div className="vt-result">
                  <span className="vt-result__l">
                    <span>Ориентировочно</span>
                    <b>38 400 ₽</b>
                  </span>
                  <span className="vt-send" data-target="send" data-sent={s.sent || undefined}>
                    <Swap2 on={s.sent} a="Отправить заявку" b="Заявка отправлена" />
                  </span>
                </div>
              </Collapse>
              <div className="vt-more">
                <b>Как рассчитать стоимость оклейки</b>
              </div>
            </div>
            <span className="vt-rest" data-target="rest" />
          </div>
        )
        return compact ? (
          <>
            <div className="vt-win vt-win--c ss-window">{page}</div>
            <div className="vt-seo vt-seo--c" data-on={s.seo || undefined}>
              <span className="vt-seo__l">Рост органики с 2019</span>
              <span className="vt-seo__n">
                <Swap2 on={s.seo} a="×1" b="×1000" />
              </span>
            </div>
          </>
        ) : (
          <>
            <div className="vt-win ss-window">
              <div className="vt-bar">
                <span />
                <span />
                <span />
                <em>vinyl-tm.ru/services/okleyka-auto/kalkulyator</em>
              </div>
              {page}
            </div>
            <Phone width={200} frame="pro" className="vt-phone">
              <div className="vt-ph">
                <img src={logo} alt="" className="vt-ph__logo" />
                <div className="vt-seo" data-on={s.seo || undefined}>
                  <span className="vt-seo__l">Рост органики с 2019</span>
                  <span className="vt-seo__n">
                    <Swap2 on={s.seo} a="×1" b="×1000" />
                  </span>
                  <Chart data={VISITS} width={290} height={130} show={s.seo} className="vt-chart" />
                  <span className="vt-seo__y">
                    <span>2019</span>
                    <span>сейчас</span>
                  </span>
                </div>
                <div className="vt-ph__row">
                  <span className="vt-ph__k">ТОП-10 Яндекса</span>
                  <b>3 000+</b>
                </div>
                <div className="vt-ph__row">
                  <span className="vt-ph__k">Страниц на сайте</span>
                  <b>2 000+</b>
                </div>
              </div>
            </Phone>
          </>
        )
      }}
    </Stage>
  )
}
