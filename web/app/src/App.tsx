import { useEffect, useState } from 'react'
import { AppShell } from './components/AppShell'
import { Dashboard } from './screens/Dashboard'
import { travelService } from './services'
import type { AgentAction, Trip } from './types'

interface DashboardData {
  trip: Trip
  actions: AgentAction[]
}

function App() {
  const [data, setData] = useState<DashboardData | null>(null)

  useEffect(() => {
    void Promise.all([travelService.getTrips(), travelService.getTimeline('uuid')]).then(([allTrips, actions]) => {
      const trip = allTrips[0]
      if (trip) setData({ trip, actions })
    })
  }, [])

  return (
    <AppShell>
      {data ? (
        <Dashboard actions={data.actions} timelinePaceMs={850} trip={data.trip} />
      ) : (
        <div className="h-80 animate-pulse rounded-lg bg-surface-container" aria-label="Loading trip" />
      )}
    </AppShell>
  )
}

export default App
