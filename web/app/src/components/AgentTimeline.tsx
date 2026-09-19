import { useEffect, useState } from 'react'
import { formatUtc } from '../lib/format'
import type { AgentAction } from '../types'

interface AgentTimelineProps {
  actions: AgentAction[]
  paceMs?: number
}

/** Null renders as nothing: no `record()` call site sets a duration yet, and "null ms" is worse than silence. */
function formatDuration(durationMs: number | null) {
  if (durationMs == null) return ''
  return durationMs < 1000 ? `${durationMs} ms` : `${(durationMs / 1000).toFixed(1)} s`
}

export function AgentTimeline({ actions, paceMs = 850 }: AgentTimelineProps) {
  const [visibleCount, setVisibleCount] = useState(Math.min(1, actions.length))

  useEffect(() => {
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    const firstVisibleCount = reduceMotion || paceMs <= 0 ? actions.length : Math.min(1, actions.length)
    const timers = [window.setTimeout(() => setVisibleCount(firstVisibleCount), 0)]
    if (!reduceMotion && paceMs > 0) actions.slice(1).forEach((_, index) => timers.push(
      window.setTimeout(() => setVisibleCount(index + 2), paceMs * (index + 1)),
    ))
    return () => timers.forEach(window.clearTimeout)
  }, [actions, paceMs])

  return (
    <section className="rounded-lg border border-outline-variant/70 bg-surface-container-lowest p-6 shadow-card" aria-labelledby="timeline-heading">
      <div className="flex flex-col gap-3 border-b border-outline-variant/60 pb-5 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="font-mono text-[10px] font-semibold uppercase tracking-[0.18em] text-primary">Autonomous recovery</p>
          <h2 id="timeline-heading" className="mt-2 text-2xl font-bold tracking-tight">Agent timeline</h2>
        </div>
        <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-on-surface-variant" aria-live="polite">
          {visibleCount} of {actions.length} stages visible
        </p>
      </div>

      <ol className="mt-6 space-y-0">
        {actions.slice(0, visibleCount).map((action, index) => {
          const failed = action.stage === 'FAILED'
          const latest = index === visibleCount - 1

          return (
            <li className="grid grid-cols-[auto_1fr] gap-4" key={action.id}>
              <div className="flex flex-col items-center" aria-hidden="true">
                <span
                  className={`mt-1 grid size-7 place-items-center rounded-full border-4 border-white text-xs text-white shadow-card ${
                    failed ? 'bg-error' : latest ? 'bg-primary animate-pulse motion-reduce:animate-none' : 'bg-emerald-500'
                  }`}
                >
                  {failed ? '!' : '✓'}
                </span>
                {index < visibleCount - 1 && <span className={`min-h-10 w-px flex-1 ${failed ? 'bg-red-200' : 'bg-outline-variant'}`} />}
              </div>

              <article className={`mb-4 rounded-md border p-4 ${failed ? 'border-red-200 bg-red-50' : 'border-outline-variant/60 bg-surface-container-low'}`}>
                <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <p className={`font-mono text-[10px] font-semibold uppercase tracking-[0.16em] ${failed ? 'text-red-700' : 'text-primary'}`}>
                      {action.stage.replaceAll('_', ' ')}
                    </p>
                    <h3 className={`mt-1 font-semibold ${failed ? 'text-red-900' : 'text-on-surface'}`}>{action.headline}</h3>
                  </div>
                  <div className="shrink-0 text-left font-mono text-[10px] leading-5 text-on-surface-variant sm:text-right">
                    <time dateTime={action.at}>{formatUtc(action.at)}</time>
                    <span className="block">{formatDuration(action.duration_ms)}</span>
                  </div>
                </div>
              </article>
            </li>
          )
        })}
      </ol>
    </section>
  )
}
