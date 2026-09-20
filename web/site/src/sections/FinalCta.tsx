import { Icon } from '../components/Icon'
import { useReveal } from '../lib/useReveal'
import { appLink } from '../lib/links'

export function FinalCta() {
  const [ref, visible] = useReveal<HTMLElement>()

  return (
    <section
      className="reveal-on-scroll w-full bg-white px-6 py-20 md:px-10"
      data-visible={visible}
      id="get-started"
      ref={ref}
    >
      <div className="group relative mx-auto max-w-[1140px] overflow-hidden rounded-3xl bg-[#0A2540] p-10 text-center text-white shadow-xl md:p-16">
        <div className="pointer-events-none absolute -bottom-24 left-1/2 size-96 -translate-x-1/2 rounded-full bg-[#0284C7]/30 blur-3xl transition-transform duration-700 group-hover:scale-125" />
        <div className="pointer-events-none absolute -top-24 right-10 size-72 rounded-full bg-[#0284C7]/20 blur-2xl" />
        <div className="relative z-10 mx-auto max-w-2xl">
          <h2 className="mb-4 font-display text-[36px] leading-[44px] tracking-tight text-white sm:text-[44px] sm:leading-[52px]">
            Take the stress out of your next business trip.
          </h2>
          <p className="mb-8 text-base leading-relaxed text-slate-300 sm:text-lg">
            Open the dashboard, simulate a cancellation on a seeded trip, and watch the agent work
            through it one timeline entry at a time.
          </p>
          <div className="mb-5 flex flex-col items-center justify-center gap-4 sm:flex-row">
            <a
              className="shimmer-btn group/cta inline-flex w-full items-center justify-center gap-2 rounded-xl bg-[#0284C7] px-8 py-4 text-base font-semibold text-white shadow-lg shadow-[#0284C7]/40 transition-all duration-150 hover:-translate-y-0.5 hover:bg-[#0369A1] hover:shadow-xl hover:shadow-[#0284C7]/45 active:scale-[0.97] sm:w-auto"
              href={appLink('/signup')}
            >
              <span>Create your account</span>
              <Icon
                className="text-[18px] transition-transform duration-200 group-hover/cta:translate-x-1"
                name="arrow_forward"
              />
            </a>
          </div>
          <p className="font-mono text-xs text-slate-400">
            Prototype • Three seeded travellers • Mock providers by default
          </p>
        </div>
      </div>
    </section>
  )
}
