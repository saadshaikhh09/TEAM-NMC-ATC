import { useEffect, useRef, useState, type RefObject } from 'react'

/** Distance above the viewport bottom at which an element counts as arrived. */
const TRIGGER_INSET = 40

/**
 * Reports the first time its element reaches the viewport, then stops listening.
 *
 * Deliberately a scroll listener rather than IntersectionObserver: the observer
 * only reports threshold *crossings*, so a jump — Cmd+End, an in-page anchor
 * (this page has three in the nav), a browser-restored scroll position — moves an
 * element from "below the fold" straight to "above the fold" without ever
 * intersecting, no callback fires, and the element keeps `opacity: 0` for good.
 * A landing page that silently hides half its content after an anchor click is a
 * worse trade than a handful of getBoundingClientRect calls.
 *
 * The animation lives in `.reveal-on-scroll` (site.css) so prefers-reduced-motion
 * can switch it off in one place.
 */
export function useReveal<T extends HTMLElement>(): [RefObject<T | null>, boolean] {
  const ref = useRef<T>(null)
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

  return [ref, visible]
}
