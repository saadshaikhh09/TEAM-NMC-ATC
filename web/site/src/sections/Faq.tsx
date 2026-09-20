import { useId, useState } from 'react'
import { Icon } from '../components/Icon'
import { Reveal } from '../components/Reveal'

const QUESTIONS = [
  {
    q: 'How does ATC find out a flight was cancelled?',
    a: 'It polls a flight status API on a schedule that tightens as departure approaches — twice daily beyond a week out, every six hours inside a week, every fifteen minutes in the last day. When a poll returns CANCELLED or DELAYED where it did not before, that becomes a disruption. There is no privileged feed and no early warning: ATC learns at the same moment the status API does. What it saves you is the part after that.',
  },
  {
    q: 'What happens if no option satisfies my constraints?',
    a: 'Nothing is booked. The plan is still written and published, because the list of what was rejected and why is the useful part, and the trip is escalated as a recovery failure for a human to pick up. There is no rail booking and no automatic airport hotel — those are not built.',
  },
  {
    q: 'Does it book without asking me?',
    a: 'Only under a limit you set. Each traveller has an auto-approve threshold for the net cost change. Under it, the plan executes on its own. Over it — or when the plan bumps into a hard constraint — the trip parks in AWAITING_APPROVAL with the ranked options and the rejections on screen, and waits for you to approve or reject.',
  },
  {
    q: 'How are hotel dates handled when the new flight lands later?',
    a: 'The extra night is priced into the option before ranking, so a cheaper flight that costs you a hotel night does not win on fare alone. If the plan executes, the booking is cancelled and rebooked at the new dates — the hotel API has no date-change call, so that round trip is the change. It talks to the provider, not to the hotel front desk.',
  },
  {
    q: 'What is real in this demo and what is mocked?',
    a: 'The state machine, the constraint filter, the ranking, the approval gate, the audit timeline and the WebSocket are all real and tested. Flight search and booking run against Duffel in test mode; hotels run against the LiteAPI/Nuitee sandbox; flight status can run against AeroDataBox or AviationStack. The demo ships with DEMO_MODE=true, which forces mock providers so a rehearsal cannot spend the 500-call monthly quota.',
  },
  {
    q: 'Does it send WhatsApp or SMS alerts?',
    a: 'No. Notifications are in-app only: the trip timeline updates live over a WebSocket while the dashboard is open. There is no messaging integration, no calendar write, and no wallet pass.',
  },
]

export function Faq() {
  // Single-open: two answers side by side in a column this narrow means the
  // reader loses which question they were on.
  const [openIndex, setOpenIndex] = useState(0)
  const baseId = useId()

  return (
    <section className="w-full bg-[#F8FAFC] px-6 py-24 md:px-10" id="faq">
      <div className="mx-auto max-w-[840px]">
        <Reveal className="mb-16 text-center">
          <span className="mb-2 block font-mono text-[12px] font-bold uppercase tracking-wider text-[#0284C7]">
            Clarifications
          </span>
          <h2 className="mb-4 font-display text-[36px] leading-[48px] tracking-tight text-[#0A2540] sm:text-[40px]">
            Frequently asked questions
          </h2>
          <p className="text-base text-[#64748B]">
            Including what the agent does not do.
          </p>
        </Reveal>

        <div className="flex flex-col gap-4">
          {QUESTIONS.map((item, index) => {
            const isOpen = index === openIndex
            const panelId = `${baseId}-panel-${index}`
            const buttonId = `${baseId}-button-${index}`

            return (
              <Reveal
                className={`faq-item rounded-xl border border-[#64748B]/20 bg-white p-6 shadow-sm transition-all duration-200 hover:border-[#0284C7]/50 ${
                  isOpen ? 'is-open' : ''
                }`}
                delayMs={index * 70}
                key={item.q}
              >
                <h3>
                  <button
                    aria-controls={panelId}
                    aria-expanded={isOpen}
                    className="flex w-full cursor-pointer items-center justify-between gap-3 text-left focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0284C7]"
                    id={buttonId}
                    onClick={() => setOpenIndex(isOpen ? -1 : index)}
                    type="button"
                  >
                    <span className="text-base font-semibold text-[#0A2540] sm:text-lg">
                      {item.q}
                    </span>
                    <Icon className="faq-chevron shrink-0 text-[#0284C7]" name="expand_more" />
                  </button>
                </h3>
                {/* The panel animates through grid-template-rows rather than the
                    `hidden` attribute, so `inert` is what actually keeps a
                    collapsed answer out of the tab order and the a11y tree. */}
                <div className="faq-content">
                  <div aria-labelledby={buttonId} className="faq-inner" id={panelId} role="region">
                    <p
                      className="mt-4 border-t border-[#64748B]/15 pt-3 text-sm leading-relaxed text-[#64748B]"
                      inert={!isOpen}
                    >
                      {item.a}
                    </p>
                  </div>
                </div>
              </Reveal>
            )
          })}
        </div>
      </div>
    </section>
  )
}
