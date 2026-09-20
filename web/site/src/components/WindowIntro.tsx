import { useEffect, useRef } from 'react'

const easeInOutCubic = (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2)
const clamp01 = (n: number) => Math.min(Math.max(n, 0), 1)

/** Fraction of the scroll at which the porthole has finished opening. */
const GROW_END = 0.72
/** Fraction by which the display copy has faded out. */
const COPY_END = 0.35

/**
 * The plane window that opens onto the sky before the page proper begins.
 *
 * A 280vh section with a sticky viewport-height layer inside it: scrolling the
 * section scrubs the porthole open. The hole is a CSS mask radial-gradient whose
 * radius is a custom property, so there is no image to load and it stays sharp at
 * any viewport size.
 *
 * Every per-frame value is written straight to the DOM as a style property
 * rather than through state — a setState per scroll frame would re-render the
 * whole landing page sixty times a second. The header's fade-in rides on the
 * same pass via `--nav-opacity` on the root element, which is why the two
 * components need no shared state at all.
 *
 * The layer is not faded out at the end. Fading it reveals this section's own
 * background, not the hero — sticky positioning keeps the layer inside its
 * parent — so a fade bought ~900px of flat colour between the intro and the
 * page. Letting the open window scroll away instead hands over seamlessly: by
 * the time it releases, the porthole is gone and the bottom of the sky gradient
 * is already the hero's background.
 */
export function WindowIntro() {
  const sectionRef = useRef<HTMLElement>(null)
  const cabinRef = useRef<HTMLDivElement>(null)
  const rimRef = useRef<HTMLDivElement>(null)
  const copyRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Reduced motion hides the section in CSS and pins --nav-opacity to 1;
    // running the handler would only fight those rules with inline styles.
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return

    const section = sectionRef.current
    const cabin = cabinRef.current
    const rim = rimRef.current
    const copy = copyRef.current
    if (!section || !cabin || !rim || !copy) return

    const update = () => {
      const total = section.offsetHeight - window.innerHeight
      const progress = total > 0 ? clamp01(-section.getBoundingClientRect().top / total) : 0

      const minR = Math.min(window.innerWidth, window.innerHeight) * 0.12
      const maxR = Math.hypot(window.innerWidth, window.innerHeight) / 2 + 120
      const grow = Math.min(progress / GROW_END, 1)
      const radius = minR + (maxR - minR) * easeInOutCubic(grow)

      cabin.style.setProperty('--window-r', `${radius}px`)
      rim.style.width = `${radius * 2}px`
      rim.style.height = `${radius * 2}px`
      // The rim only disappears in the last sliver of the growth, once it is
      // already off-screen — fading it earlier makes the glass look like it melts.
      rim.style.opacity = String(grow > 0.94 ? Math.max(1 - (grow - 0.94) / 0.06, 0) : 1)

      copy.style.opacity = String(Math.max(1 - progress / COPY_END, 0))

      const navFade = clamp01((progress - 0.35) / 0.3)
      const root = document.documentElement.style
      root.setProperty('--nav-opacity', String(navFade))
      // Keeps the nav out of the tab order and out of reach of the pointer
      // while it is still transparent.
      root.setProperty('--nav-visibility', navFade > 0 ? 'visible' : 'hidden')
    }

    // One frame in flight at a time: a bare rAF per scroll event queues a
    // backlog that keeps painting after the user has stopped.
    let queued = false
    const onScroll = () => {
      if (queued) return
      queued = true
      requestAnimationFrame(() => {
        queued = false
        update()
      })
    }

    update()
    window.addEventListener('scroll', onScroll, { passive: true })
    window.addEventListener('resize', onScroll, { passive: true })

    return () => {
      window.removeEventListener('scroll', onScroll)
      window.removeEventListener('resize', onScroll)
    }
  }, [])

  return (
    <section aria-hidden="true" id="window-intro" ref={sectionRef}>
      <div id="window-intro-sticky">
        <div id="intro-sky">
          <div
            className="intro-cloud"
            style={{
              top: '16%',
              left: '6%',
              width: 260,
              height: 90,
              animation: 'cloud-drift-a 42s ease-in-out infinite alternate',
            }}
          />
          <div
            className="intro-cloud"
            style={{
              top: '30%',
              left: '58%',
              width: 340,
              height: 110,
              animation: 'cloud-drift-b 55s ease-in-out infinite alternate',
            }}
          />
          <div
            className="intro-cloud"
            style={{
              top: '58%',
              left: '18%',
              width: 220,
              height: 80,
              animation: 'cloud-drift-a 48s ease-in-out infinite alternate',
            }}
          />
          <div
            className="intro-cloud"
            style={{
              top: '70%',
              left: '62%',
              width: 300,
              height: 100,
              animation: 'cloud-drift-b 60s ease-in-out infinite alternate',
            }}
          />
          <div
            className="intro-cloud"
            style={{
              top: '44%',
              left: '38%',
              width: 180,
              height: 70,
              animation: 'cloud-drift-a 36s ease-in-out infinite alternate',
            }}
          />
        </div>
        <div id="intro-cabin" ref={cabinRef} />
        <div id="intro-rim" ref={rimRef} />
        <div id="intro-copy" ref={copyRef}>
          <div className="flex items-start justify-start">
            <p className="intro-line">
              We detect it <em>first.</em>
            </p>
          </div>
          <div className="flex flex-wrap items-end justify-between gap-6">
            <span id="intro-scroll-cue">Scroll to see how ↓</span>
            <p className="intro-line ml-auto text-right">
              We fix it <em>for you.</em>
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}
