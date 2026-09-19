const appUrl = import.meta.env.VITE_APP_URL

function App() {
  return (
    <div className="site-theme min-h-screen bg-white text-navy">
      <header className="border-b border-slate-200 bg-navy text-white">
        <nav className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-8" aria-label="Main">
          <a className="flex items-center gap-3 font-semibold" href="/">
            <span className="grid size-9 place-items-center rounded-lg bg-sky font-mono text-sm">ATC</span>
            <span>Travel Concierge</span>
          </a>
          <a className="rounded-lg bg-sky px-4 py-2 text-sm font-semibold hover:bg-sky/90" href={appUrl}>
            Open app
          </a>
        </nav>
      </header>
      <main className="mx-auto grid min-h-[calc(100vh-4rem)] max-w-6xl place-items-center px-4 py-16 sm:px-8">
        <section className="max-w-3xl text-center">
          <p className="font-mono text-xs font-semibold uppercase tracking-[0.16em] text-sky">Site · Port 5173</p>
          <h1 className="mt-4 font-display text-5xl leading-tight sm:text-6xl">Travel disruptions, resolved around you.</h1>
          <p className="mx-auto mt-5 max-w-xl text-slate-600">
            The marketing surface is scaffolded and remains independent from the product app.
          </p>
        </section>
      </main>
    </div>
  )
}

export default App
