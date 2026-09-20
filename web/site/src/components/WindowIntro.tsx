import { useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { appLink } from '../lib/links'

const clamp = (value: number) => Math.min(Math.max(value, 0), 1)

export function WindowIntro() {
  const sectionRef = useRef<HTMLElement>(null)
  const imageRef = useRef<HTMLImageElement>(null)
  const copyRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) return
    const section = sectionRef.current
    const image = imageRef.current
    const copy = copyRef.current
    if (!section || !image || !copy) return
    let queued = false
    const update = () => {
      queued = false
      const total = Math.max(section.offsetHeight - innerHeight, 1)
      const progress = clamp(-section.getBoundingClientRect().top / total)
      image.style.transform = `scale(${1 + progress * 3.5})`
      image.style.opacity = String(clamp(1 - (progress - 0.62) / 0.3))
      copy.style.opacity = String(clamp(1 - progress / 0.42))
      copy.style.transform = `translateY(${-progress * 28}px)`
    }
    const schedule = () => { if (!queued) { queued = true; requestAnimationFrame(update) } }
    update()
    addEventListener('scroll', schedule, { passive: true })
    addEventListener('resize', schedule, { passive: true })
    return () => { removeEventListener('scroll', schedule); removeEventListener('resize', schedule) }
  }, [])

  return (
    <section className="window-sequence" ref={sectionRef}>
      <div className="window-sticky">
        <div className="window-sky" />
        <img alt="View through an aircraft cabin window into a clear blue sky" className="window-asset" ref={imageRef} src="/assets/aircraft-window.png" />
        <div className="window-copy" ref={copyRef}>
          <p className="intro-kicker">AUTONOMOUS TRAVEL CONCIERGE</p>
          <h1><span>When plans break,</span><em>your journey keeps moving.</em></h1>
          <p className="intro-body">ATC watches the itinerary, explains every decision, and moves only within the limits you set.</p>
          <div className="intro-actions">
            <a className="button-primary" href={appLink('/signup')}>Get started</a>
            <Link className="button-glass" to="/how-it-works">See how it works</Link>
          </div>
          <span className="scroll-cue">Scroll through the window ↓</span>
        </div>
      </div>
    </section>
  )
}
