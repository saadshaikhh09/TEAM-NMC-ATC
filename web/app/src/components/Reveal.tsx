import { useEffect, useRef, useState, type ReactNode } from 'react'

interface RevealProps {
  children: ReactNode
  /** Stagger siblings so a row of cards arrives in sequence, not all at once. */
  delayMs?: number
  className?: string
}

/** Distance above the viewport bottom at which a card counts as arrived. */
const TRIGGER_INSET = 48

/**
 * Reveals its children the first time they reach the viewport, then stays put.
 *
 * Deliberately a scroll listener rather than IntersectionObserver: the observer
 * only reports threshold *crossings*, so a jump — Cmd+End, an anchor, a restored
 * scroll position — skips straight past a card without ever firing, and the card
 * stays invisible for good. On a dashboard whose job is surfacing flight
 * disruptions, silently hiding content is a much worse failure than a handful of
 * getBoundingClientRect calls. Each card drops its listeners once revealed.
 *
 * The animation lives in `.reveal` (index.css) so `prefers-reduced-motion` can
 * switch it off in one place.
 */
export function Reveal({ children, delayMs = 0, className = '' }: RevealProps) {
  const ref = useRef<HTMLDivElement>(null)
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    if (visible) return
    const node = ref.current
    if (!node) return

    const check = () => {
      if (node.getBoundingClientRect().top < window.innerHeight - TRIGGER_INSET) setVisible(true)
    }

    // rAF: runs after first layout, and keeps the initial check off the effect's
    // synchronous path so it cannot cascade an extra render.
    const frame = requestAnimationFrame(check)
    window.addEventListener('scroll', check, { passive: true })
    window.addEventListener('resize', check, { passive: true })

    return () => {
      cancelAnimationFrame(frame)
      window.removeEventListener('scroll', check)
      window.removeEventListener('resize', check)
    }
  }, [visible])

  return (
    <div
      className={`reveal ${className}`}
      data-visible={visible}
      ref={ref}
      style={delayMs ? { transitionDelay: `${delayMs}ms` } : undefined}
    >
      {children}
    </div>
  )
}
