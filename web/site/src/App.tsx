import { SiteFooter } from './components/SiteFooter'
import { SiteHeader } from './components/SiteHeader'
import { WindowIntro } from './components/WindowIntro'
import { Faq } from './sections/Faq'
import { Features } from './sections/Features'
import { FinalCta } from './sections/FinalCta'
import { Hero } from './sections/Hero'
import { HowItWorks } from './sections/HowItWorks'
import { TrustStrip } from './sections/TrustStrip'

function App() {
  return (
    <div className="site-theme bg-[#F8FAFC] text-[#0A2540] antialiased selection:bg-[#0284C7]/20">
      {/* Nearly three viewport heights of scroll intro sit between the top of
          the page and the first real content. Without this, a keyboard user has
          no way past it. */}
      <a
        className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[60] focus:rounded-lg focus:bg-[#0A2540] focus:px-4 focus:py-2 focus:text-sm focus:font-semibold focus:text-white"
        href="#top"
      >
        Skip to content
      </a>

      <WindowIntro />
      <SiteHeader />

      {/* No top padding here: the hero owns the clearance for the fixed header
          (pt-36 = 5rem of header + its own 4rem), so its gradient starts flush
          against the intro instead of behind a strip of flat page colour. */}
      <main className="w-full bg-[#F8FAFC]">
        <Hero />
        <TrustStrip />
        <HowItWorks />
        <Features />
        <Faq />
        <FinalCta />
      </main>

      <SiteFooter />
    </div>
  )
}

export default App
