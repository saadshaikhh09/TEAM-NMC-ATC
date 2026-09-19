import { useEffect, useState } from 'react'
import { AppShell } from './components/AppShell'
import { Dashboard } from './screens/Dashboard'
import { travelService } from './services'
import type { Trip } from './types'

function App() {
  const [trip, setTrip] = useState<Trip | null>(null)

  useEffect(() => {
    void travelService.getTrips().then(([firstTrip]) => setTrip(firstTrip ?? null))
  }, [])

  return (
    <AppShell>
      {trip ? (
        <Dashboard trip={trip} />
      ) : (
        <div className="h-80 animate-pulse rounded-lg bg-surface-container" aria-label="Loading trip" />
      )}
    </AppShell>
  )
}

export default App
