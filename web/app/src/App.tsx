const siteUrl = import.meta.env.VITE_SITE_URL

function App() {
  return (
    <div className="app-theme min-h-screen bg-background text-on-surface">
      <header className="border-b border-outline-variant/60 bg-navy text-white">
        <nav className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-8" aria-label="Product">
          <a className="flex items-center gap-3 font-semibold" href={siteUrl}>
            <span className="grid size-9 place-items-center rounded-lg bg-sky font-mono text-sm">ATC</span>
            <span>Travel Concierge</span>
          </a>
          <span className="rounded-full bg-white/10 px-3 py-1 font-mono text-xs uppercase tracking-wider">
            Mock mode
          </span>
        </nav>
      </header>
      <main className="mx-auto grid min-h-[calc(100vh-4rem)] max-w-6xl place-items-center px-4 py-16 sm:px-8">
        <section className="w-full max-w-2xl rounded-lg border border-outline-variant bg-surface-container-lowest p-8 shadow-raised">
          <p className="font-mono text-xs font-semibold uppercase tracking-[0.16em] text-primary">App · Port 5174</p>
          <h1 className="mt-3 text-4xl font-bold tracking-tight">Your journey, monitored.</h1>
          <p className="mt-4 max-w-xl text-on-surface-variant">
            The product surface is ready for contract-shaped mock trips, recovery plans, and timeline actions.
          </p>
        </section>
      </main>
    </div>
  )
}

export default App
