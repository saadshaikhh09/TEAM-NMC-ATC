import { useId, type ReactNode } from 'react'

interface TooltipProps {
  /** The explanation. Keep it to one sentence — this is a hint, not a help page. */
  label: string
  children: ReactNode
}

/**
 * Hover/focus tooltip, CSS-only.
 *
 * The trigger is focusable and wired with `aria-describedby`, so the hint reaches
 * keyboard and screen-reader users rather than only a mouse. No popover library:
 * these all sit inside cards with room above them, so the positioning a library
 * would buy us is positioning we do not need.
 */
export function Tooltip({ label, children }: TooltipProps) {
  const id = useId()

  return (
    <span className="group/tip relative inline-flex">
      <span
        aria-describedby={id}
        className="inline-flex cursor-help items-center gap-1 underline decoration-dotted decoration-from-font underline-offset-4 outline-none focus-visible:rounded focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2"
        tabIndex={0}
      >
        {children}
      </span>
      {/* Width is clamped to the viewport so a tooltip near the right edge cannot
          widen the page. AppShell clips whatever still overhangs. */}
      <span
        className="pointer-events-none absolute bottom-full left-1/2 z-30 mb-2 w-max max-w-[min(16rem,calc(100vw-2rem))] -translate-x-1/2 rounded-md bg-navy px-3 py-2 text-xs font-medium leading-5 text-white opacity-0 shadow-raised transition-opacity duration-150 group-focus-within/tip:opacity-100 group-hover/tip:opacity-100"
        id={id}
        role="tooltip"
      >
        {label}
        <span
          aria-hidden="true"
          className="absolute left-1/2 top-full size-2 -translate-x-1/2 -translate-y-1 rotate-45 bg-navy"
        />
      </span>
    </span>
  )
}
