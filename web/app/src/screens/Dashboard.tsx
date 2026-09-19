import { useState } from 'react'
import { AgentTimeline } from '../components/AgentTimeline'
import { ApprovalModal } from '../components/ApprovalModal'
import { RejectionPanel } from '../components/RejectionPanel'
import { TripCard } from '../components/TripCard'
import type { AgentAction, RecoveryPlan, Trip } from '../types'

interface DashboardProps {
  trip: Trip
  actions: AgentAction[]
  plan: RecoveryPlan
  onApprove: () => Promise<void>
  onReject: () => Promise<void>
  timelinePaceMs?: number
}

export function Dashboard({ trip, actions, plan, onApprove, onReject, timelinePaceMs }: DashboardProps) {
  const [approvalOpen, setApprovalOpen] = useState(false)

  const decide = async (decision: () => Promise<void>) => {
    await decision()
    setApprovalOpen(false)
  }

  return (
    <section aria-labelledby="dashboard-title">
      <div className="mb-8 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="font-mono text-xs font-semibold uppercase tracking-[0.16em] text-primary">Journey control</p>
          <h1 id="dashboard-title" className="mt-2 text-3xl font-bold tracking-tight sm:text-4xl">
            Your trip, handled.
          </h1>
        </div>
        <p className="max-w-md text-sm leading-6 text-on-surface-variant">
          Contract-shaped mock data keeps this dashboard available without the API or network.
        </p>
      </div>
      <div className="space-y-8">
        <TripCard trip={trip} />
        <RejectionPanel rejections={plan.rejections} />
        <section className={`flex flex-col gap-5 rounded-lg border p-6 shadow-card sm:flex-row sm:items-center sm:justify-between ${plan.state === 'APPROVED' ? 'border-emerald-200 bg-emerald-50' : plan.state === 'REJECTED' ? 'border-red-200 bg-red-50' : 'border-primary/20 bg-primary-fixed/45'}`}>
          <div>
            <p className="font-mono text-[10px] font-semibold uppercase tracking-[0.18em] text-primary">Recovery plan · {plan.state}</p>
            <h2 className="mt-2 text-xl font-bold">
              {plan.state === 'APPROVED' ? 'Plan approved and ready to execute.' : plan.state === 'REJECTED' ? 'Plan rejected. No action was taken.' : plan.approval_reason}
            </h2>
          </div>
          {plan.state === 'AWAITING_APPROVAL' && (
            <button className="shrink-0 rounded-lg bg-primary px-5 py-3 font-semibold text-white shadow-card hover:bg-primary-container" onClick={() => setApprovalOpen(true)} type="button">
              Review recovery plan
            </button>
          )}
        </section>
        <AgentTimeline actions={actions} paceMs={timelinePaceMs} />
      </div>
      {approvalOpen && (
        <ApprovalModal
          onApprove={() => decide(onApprove)}
          onClose={() => setApprovalOpen(false)}
          onReject={() => decide(onReject)}
          plan={plan}
        />
      )}
    </section>
  )
}
