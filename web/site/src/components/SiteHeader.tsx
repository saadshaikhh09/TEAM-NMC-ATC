import { useEffect, useRef } from 'react'
import { Icon } from './Icon'

const appUrl = import.meta.env.VITE_APP_URL

const NAV_LINKS = [
  { href: '#how-it-works', label: 'How it works' },
  { href: '#features', label: 'Features' },
  { href: '#faq', label: 'FAQ' },
]

/**
 * Fixed nav plus the scroll-linked progress line along its bottom edge.
 *
 * Opacity and visibility come from `--nav-opacity` / `--nav-visibility`, which
 * WindowIntro writes as the porthole opens — the header stays out of the way
 * until the intro has handed the page over. The progress bar's width is set on
 * the node directly for the same reason the intro's values are: a state update
 * per scroll frame would re-render the page under the user's cursor.
 */
export function SiteHeader() {
  const headerRef = useRef<HTMLElement>(null)
  const barRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const update = () => {
      const scrollTop = window.scrollY
      const scrollable = document.documentElement.scrollHeight - window.innerHeight

      headerRef.current?.classList.toggle('shadow-md', scrollTop > 20)

      if (barRef.current && scrollable > 0) {
        barRef.current.style.width = `${Math.min(Math.max((scrollTop / scrollable) * 100, 0), 100)}%`
      }
    }

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
    <header
      className="fixed inset-x-0 top-0 z-50 border-b border-[#64748B]/15 bg-white/90 backdrop-blur-xl transition-shadow duration-300"
      ref={headerRef}
      style={{ opacity: 'var(--nav-opacity)', visibility: 'var(--nav-visibility)' as never }}
    >
      <div className="mx-auto flex h-20 max-w-[1280px] items-center justify-between px-6 md:px-10">
        <a className="group flex items-center gap-3" href="#top">
          <span className="flex size-10 items-center justify-center rounded-xl bg-[#0A2540] text-white shadow-sm transition-all duration-200 group-hover:scale-105 group-hover:bg-[#0284C7] group-active:scale-95">
            <Icon className="text-[22px]" name="connecting_airports" />
          </span>
          <span className="text-lg font-bold tracking-tight text-[#0A2540]">ATC</span>
          <span className="hidden rounded-full bg-[#E0F2FE] px-2.5 py-0.5 font-mono text-[11px] font-semibold uppercase tracking-wider text-[#0284C7] transition-colors duration-200 group-hover:bg-[#0284C7] group-hover:text-white sm:inline">
            Concierge
          </span>
        </a>

        <nav aria-label="Main" className="hidden items-center gap-8 md:flex">
          {NAV_LINKS.map((link) => (
            <a
              className="nav-link-hover py-1 text-sm font-medium text-[#64748B] transition-colors hover:text-[#0A2540]"
              href={link.href}
              key={link.href}
            >
              {link.label}
            </a>
          ))}
        </nav>

        <div className="flex items-center gap-4">
          {/* No "Log in": the app has no auth. It would be the first thing on
              the page that isn't true. */}
          <a
            className="shimmer-btn inline-flex items-center justify-center whitespace-nowrap rounded-xl bg-[#0284C7] px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition-all duration-150 hover:-translate-y-0.5 hover:bg-[#0369A1] hover:shadow-md active:scale-[0.97] sm:px-5"
            href={appUrl}
          >
            Open the dashboard
          </a>
        </div>
      </div>

      {/* Scroll-linked starlight progress line. */}
      <div className="pointer-events-none absolute inset-x-0 bottom-0 h-[2.5px] overflow-visible">
        <div
          className="relative h-full w-0 bg-gradient-to-r from-[#0284C7] via-[#38BDF8] to-[#67e8f9] shadow-[0_0_12px_2px_rgba(56,189,248,0.7),0_0_4px_1px_rgba(2,132,199,0.9)] will-change-[width]"
          ref={barRef}
        >
          <span className="starlight-head absolute right-0 top-1/2 flex -translate-y-1/2 translate-x-1/2 items-center justify-center">
            <span className="size-3 rounded-full bg-white shadow-[0_0_10px_3px_rgba(56,189,248,1),0_0_20px_6px_rgba(14,165,233,0.8)]" />
            <span className="absolute h-[1.5px] w-6 bg-white blur-[0.5px]" />
            <span className="absolute h-6 w-[1.5px] bg-white blur-[0.5px]" />
          </span>
        </div>
      </div>
    </header>
  )
}
