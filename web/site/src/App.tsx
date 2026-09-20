import { useEffect, type ReactNode } from 'react'
import { Link, Route, Routes, useLocation } from 'react-router-dom'
import { SiteFooter } from './components/SiteFooter'
import { SiteHeader } from './components/SiteHeader'
import { WindowIntro } from './components/WindowIntro'
import { Faq } from './sections/Faq'
import { Features } from './sections/Features'
import { FinalCta } from './sections/FinalCta'
import { Hero } from './sections/Hero'
import { HowItWorks } from './sections/HowItWorks'
import { TrustStrip } from './sections/TrustStrip'

function ScrollRestoration() {
  const { pathname } = useLocation()
  useEffect(() => {
    window.scrollTo(0, 0)
  }, [pathname])
  return null
}

function Frame({ children }: { children: ReactNode }) {
  return (
    <div className="site-theme min-h-screen bg-background text-text antialiased selection:bg-primary/20">
      <a className="skip-link" href="#main-content">Skip to content</a>
      <SiteHeader />
      {children}
      <SiteFooter />
    </div>
  )
}

function Home() {
  return (
    <Frame>
      <WindowIntro />
      <main id="main-content">
        <Hero />
        <TrustStrip />
        <Features />
        <section className="faq-teaser">
          <p className="eyebrow">Clear boundaries</p>
          <h2>Questions before you hand over the itinerary?</h2>
          <p>See what is automated, what remains simulated, and exactly when ATC asks for approval.</p>
          <Link className="button-secondary" to="/faq">Read all FAQs</Link>
        </section>
        <FinalCta />
      </main>
    </Frame>
  )
}

function HowPage() {
  return (
    <Frame>
      <main className="page-main" id="main-content">
        <section className="page-lead">
          <p className="eyebrow">Transparent by design</p>
          <h1>From disruption to recovery, five visible decisions.</h1>
          <p>Every stage writes to the audit timeline. The simulated feed starts the flow; deterministic code makes the decision.</p>
        </section>
        <HowItWorks />
      </main>
    </Frame>
  )
}

function FaqPage() {
  return <Frame><main className="page-main" id="main-content"><Faq /></main></Frame>
}

function NotFound() {
  return (
    <Frame>
      <main className="not-found" id="main-content">
        <div className="radar-orbit" aria-hidden="true"><span /><span /><span /></div>
        <p className="eyebrow">404 · Route disrupted</p>
        <h1>This flight path is not in the plan.</h1>
        <p>The route may have moved, but recovery is simple.</p>
        <Link className="button-primary" to="/">Return to ATC</Link>
      </main>
    </Frame>
  )
}

export default function App() {
  return (
    <>
      <ScrollRestoration />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/how-it-works" element={<HowPage />} />
        <Route path="/faq" element={<FaqPage />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </>
  )
}
