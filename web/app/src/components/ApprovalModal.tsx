import { useEffect, useRef, useState } from 'react'
import { formatDelta, formatInr, formatUtc } from '../lib/format'
import type { RecoveryPlan } from '../types'

interface ApprovalModalProps {
  plan: RecoveryPlan
  onApprove: () => Promise<void>
  onClose: () => void
  onReject: () => Promise<void>
}

export function ApprovalModal({ plan, onApprove, onClose, onReject }: ApprovalModalProps) {
  const chosenOption = plan.options.find((option) => option.id === plan.chosen_option_id)
  const dialogRef = useRef<HTMLElement>(null)
  const [pending, setPending] = useState<'approve' | 'reject' | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const previous = document.activeElement instanceof HTMLElement ? document.activeElement : null
    dialogRef.current?.focus()
    return () => previous?.focus()
  }, [])

  const decide = async (decision: 'approve' | 'reject') => {
    if (pending) return
    setPending(decision)
    setError(null)
    try { await (decision === 'approve' ? onApprove() : onReject()) }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'The decision could not be saved.') }
    finally { setPending(null) }
  }

  const onDialogKeyDown = (event: React.KeyboardEvent<HTMLElement>) => {
    if (event.key === 'Escape' && !pending) onClose()
    if (event.key !== 'Tab') return
    const buttons = Array.from(dialogRef.current?.querySelectorAll<HTMLButtonElement>('button:not(:disabled)') ?? [])
    if (!buttons.length) return
    const first = buttons[0], last = buttons[buttons.length - 1]
    if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus() }
    else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus() }
  }

  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-navy/60 p-4 backdrop-blur-sm" role="presentation">
      <section
        aria-labelledby="approval-heading"
        aria-modal="true"
        className="max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-xl bg-white shadow-2xl"
        onKeyDown={onDialogKeyDown}
        ref={dialogRef}
        role="dialog"
        tabIndex={-1}
      >
        <header className="flex items-start justify-between gap-5 border-b border-outline-variant/60 bg-surface-container-low px-6 py-5">
          <div>
            <p className="font-mono text-[10px] font-semibold uppercase tracking-[0.18em] text-primary">Approval required</p>
            <h2 id="approval-heading" className="mt-2 text-2xl font-bold tracking-tight">Review the recovery plan</h2>
          </div>
          <button className="grid size-9 place-items-center rounded-full border border-outline-variant text-xl text-on-surface-variant hover:bg-white" disabled={pending !== null} onClick={onClose} type="button" aria-label="Close approval modal">
            ×
          </button>
        </header>

        <div className="space-y-5 p-6">
          <div className="rounded-md border border-amber-200 bg-amber-50 p-4">
            <p className="text-xs font-semibold uppercase tracking-wide text-amber-800">Why we are asking</p>
            <p className="mt-2 font-semibold text-amber-950">{plan.approval_reason}</p>
          </div>

          {chosenOption && (
            <section className="rounded-md border border-outline-variant/60 p-5" aria-labelledby="chosen-option-heading">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="font-mono text-[10px] font-semibold uppercase tracking-[0.16em] text-primary">Chosen option</p>
                  <h3 id="chosen-option-heading" className="mt-1 text-xl font-bold">
                    {chosenOption.flight_number}
                  </h3>
                </div>
                <p className="text-lg font-bold">{formatInr(chosenOption.fare_inr)}</p>
              </div>
              <dl className="mt-5 grid gap-4 sm:grid-cols-3">
                <div>
                  <dt className="text-xs text-on-surface-variant">Departure</dt>
                  <dd className="mt-1 font-semibold">{formatUtc(chosenOption.departure)}</dd>
                </div>
                <div>
                  <dt className="text-xs text-on-surface-variant">Arrival</dt>
                  <dd className="mt-1 font-semibold">{formatUtc(chosenOption.arrival)}</dd>
                </div>
                <div>
                  <dt className="text-xs text-on-surface-variant">Journey</dt>
                  <dd className="mt-1 font-semibold">
                    {chosenOption.stops === 0 ? 'Non-stop' : `${chosenOption.stops} stop`} · {chosenOption.cabin}
                  </dd>
                </div>
              </dl>
            </section>
          )}

          <section className="grid gap-4 rounded-md bg-surface-container-low p-5 sm:grid-cols-3" aria-label="Plan cost and hotel impact">
            <div>
              <p className="text-xs text-on-surface-variant">Hotel change</p>
              <p className="mt-1 font-semibold">{plan.hotel_change?.required ? `New check-in ${plan.hotel_change.new_check_in}` : 'Not required'}</p>
            </div>
            <div>
              <p className="text-xs text-on-surface-variant">Hotel delta</p>
              <p className="mt-1 font-semibold">{formatDelta(plan.hotel_change?.cost_delta_inr ?? null, 'No hotel on this trip')}</p>
            </div>
            <div>
              <p className="text-xs text-on-surface-variant">Total cost delta</p>
              <p className="mt-1 text-lg font-bold text-primary">{formatDelta(plan.total_cost_delta_inr)}</p>
            </div>
          </section>
        </div>

        <footer className="grid gap-3 border-t border-outline-variant/60 px-6 py-5 sm:grid-cols-2">
          {error && <p className="form-error sm:col-span-2" role="alert">{error}</p>}
          <button className="rounded-lg border border-red-200 bg-red-50 px-5 py-3 font-semibold text-red-700 hover:bg-red-100 disabled:cursor-not-allowed disabled:opacity-50" disabled={pending !== null} onClick={() => void decide('reject')} type="button">
            {pending === 'reject' ? 'Rejecting…' : 'Reject plan'}
          </button>
          <button className="rounded-lg bg-primary px-5 py-3 font-semibold text-white shadow-card hover:bg-primary-container disabled:cursor-not-allowed disabled:opacity-50" disabled={pending !== null} onClick={() => void decide('approve')} type="button">
            {pending === 'approve' ? 'Approving…' : 'Approve recovery'}
          </button>
        </footer>
      </section>
    </div>
  )
}
