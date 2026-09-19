import type { Rejection } from '../types'

interface RejectionPanelProps {
  rejections: Rejection[]
}

export function RejectionPanel({ rejections }: RejectionPanelProps) {
  if (!rejections.length) return null

  return (
    <section className="overflow-hidden rounded-lg border border-amber-200 bg-amber-50 shadow-card" aria-labelledby="rejections-heading">
      <div className="border-b border-amber-200 bg-amber-100/70 px-6 py-5">
        <p className="font-mono text-[10px] font-semibold uppercase tracking-[0.18em] text-amber-800">Your rules decided first</p>
        <h2 id="rejections-heading" className="mt-2 text-2xl font-bold tracking-tight text-amber-950">
          Cheaper did not mean better.
        </h2>
      </div>
      <div className="space-y-4 p-6">
        {rejections.map((rejection) => (
          <article className="rounded-md border border-amber-200 bg-white p-5" key={`${rejection.option_id}-${rejection.rule}`}>
            <div className="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <p className="font-mono text-[10px] font-semibold uppercase tracking-[0.16em] text-amber-700">
                  Rejected · {rejection.option_id} · {rejection.rule.replaceAll('_', ' ')}
                </p>
                <h3 className="mt-2 text-xl font-bold text-amber-950">{rejection.human_reason}</h3>
              </div>
              <p className="shrink-0 rounded-full bg-amber-100 px-4 py-2 text-sm font-bold text-amber-950">
                {rejection.note}
              </p>
            </div>
          </article>
        ))}
      </div>
    </section>
  )
}
