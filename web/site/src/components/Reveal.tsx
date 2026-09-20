import type { ReactNode } from 'react'
import { useReveal } from '../lib/useReveal'

interface RevealProps {
  children: ReactNode
  /** Stagger siblings so a row of cards arrives in sequence, not all at once. */
  delayMs?: number
  /** Applied to the revealed element itself — it is the card, not a wrapper. */
  className?: string
  id?: string
}

/** Fades and lifts its card into place the first time it is scrolled to. */
export function Reveal({ children, delayMs = 0, className = '', id }: RevealProps) {
  const [ref, visible] = useReveal<HTMLDivElement>()

  return (
    <div
      className={`reveal-on-scroll ${className}`}
      data-visible={visible}
      id={id}
      ref={ref}
      style={delayMs ? { transitionDelay: `${delayMs}ms` } : undefined}
    >
      {children}
    </div>
  )
}
