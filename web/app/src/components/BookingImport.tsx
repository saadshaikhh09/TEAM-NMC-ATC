import { useId, useState } from 'react'
import type { Trip } from '../types'

interface BookingImportProps {
  /** Rejects with the API's own reason — a blank LLM chain answers 503 with words. */
  onExtract: (pastedBookingText: string) => Promise<Trip>
  /** Extraction runs on the server; the mocks have no model to stand in for it. */
  live: boolean
}

/** Deterministic, and shaped like the confirmations the seeded trip came from. */
const SAMPLE = `Your Air India booking is confirmed.

Passenger: Priya Sharma
PNR: AX91

AI131  Mumbai (BOM) -> London Heathrow (LHR)
Departs 02:30, 20 Sep 2026
Arrives 07:15, 20 Sep 2026
Economy

AI132  London Heathrow (LHR) -> Mumbai (BOM)
Departs 13:00, 25 Sep 2026
Arrives 02:40, 26 Sep 2026
Economy

Hotel: Kensington Central, London
Confirmation HTL-99213
Check in 20 Sep 2026, check out 25 Sep 2026`

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-xs text-on-surface-variant">{label}</dt>
      <dd className="mt-1 font-semibold">{value}</dd>
    </div>
  )
}

/**
 * Paste a booking email, get a structured trip back.
 *
 * This is the replacement for Gmail ingestion. The server validates the extracted
 * input first, then persists it through the same transaction as the manual form.
 */
export function BookingImport({ onExtract, live }: BookingImportProps) {
  const fieldId = useId()
  const [text, setText] = useState('')
  const [reading, setReading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<Trip | null>(null)

  const read = async () => {
    setReading(true)
    setError(null)
    try {
      setResult(await onExtract(text))
    } catch (cause) {
      setResult(null)
      setError(cause instanceof Error ? cause.message : 'Extraction did not answer.')
    } finally {
      setReading(false)
    }
  }

  return (
    <article
      aria-labelledby="import-heading"
      className="rounded-lg border border-outline-variant/70 bg-surface-container-lowest px-6 py-6 shadow-card"
    >
      <p className="font-mono text-[10px] font-semibold uppercase tracking-[0.18em] text-primary">Add a trip</p>
      <h2 className="mt-2 text-xl font-bold tracking-tight" id="import-heading">
        Paste a booking email.
      </h2>
      <p className="mt-2 max-w-xl text-sm leading-6 text-on-surface-variant">
        The concierge reads the confirmation into a structured trip — flights, hotel and dates. The
        text goes to our API and nowhere else.
      </p>

      <label className="sr-only" htmlFor={fieldId}>
        Booking confirmation text
      </label>
      <textarea
        className="mt-4 w-full rounded border border-outline-variant bg-surface-container-lowest px-3.5 py-2.5 font-mono text-xs leading-5 text-on-surface placeholder:text-on-surface-variant/70 focus:border-primary-container focus:outline-none focus:ring-2 focus:ring-primary/20 disabled:bg-surface-container-low disabled:text-on-surface-variant"
        disabled={!live}
        id={fieldId}
        onChange={(event) => setText(event.target.value)}
        placeholder="Paste the whole confirmation — carrier, flight numbers, times, hotel."
        rows={7}
        value={text}
      />

      <div className="mt-4 flex flex-wrap items-center gap-3">
        <button
          className="lift rounded-lg bg-primary px-5 py-3 font-semibold text-white shadow-card hover:bg-primary-container focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:bg-outline-variant disabled:text-on-surface-variant disabled:shadow-none"
          disabled={!live || reading || !text.trim()}
          onClick={() => void read()}
          type="button"
        >
          {reading ? 'Reading and saving…' : 'Import and monitor'}
        </button>
        <button
          className="rounded-lg px-3 py-3 text-sm font-semibold text-primary underline decoration-dotted underline-offset-4 hover:text-primary-container focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:text-on-surface-variant disabled:no-underline"
          disabled={!live || reading}
          onClick={() => {
            setText(SAMPLE)
            setError(null)
            setResult(null)
          }}
          type="button"
        >
          Use a sample booking
        </button>
      </div>

      {/* Unavailable is not a failure, so it is not printed in the error colour. */}
      {live ? (
        <p aria-live="polite" className="mt-3 min-h-5 text-sm leading-5 text-error">
          {error}
        </p>
      ) : (
        <p className="mt-3 text-sm leading-5 text-on-surface-variant">
          Booking extraction needs the API. The mocks have no model to read with.
        </p>
      )}

      {result && (
        <section
          aria-label="What the concierge read"
          className="mt-5 rounded-md border border-primary/20 bg-primary-fixed/45 px-5 py-5"
        >
          <p className="font-mono text-[10px] font-semibold uppercase tracking-[0.16em] text-primary">
            Read from your booking
          </p>
          <h3 className="mt-2 text-lg font-bold">{result.traveller_name}</h3>
          <p className="mt-1 font-mono text-sm text-on-surface-variant">
            {result.origin} <span aria-hidden="true">→</span> {result.destination}
          </p>

          <dl className="mt-4 grid grid-cols-2 gap-x-6 gap-y-4 sm:grid-cols-4">
            <Row label="Flights" value={String(result.flights.length)} />
            <Row label="Hotels" value={String(result.hotels.length)} />
            <Row
              label="Arrive by"
              value={result.constraints.hard_arrival_by_local ?? 'No deadline'}
            />
            <Row label="Cabin" value={result.constraints.cabin ?? 'Not set'} />
          </dl>

          <ul className="mt-4 space-y-2">
            {result.flights.map((flight) => (
              <li className="flex flex-wrap items-baseline gap-x-3 gap-y-1 text-sm" key={flight.id}>
                <span className="font-mono text-xs font-semibold tracking-[0.08em]">
                  {flight.flight_number}
                </span>
                <span className="font-mono text-xs text-on-surface-variant">
                  {flight.origin} <span aria-hidden="true">→</span> {flight.destination}
                </span>
                <span className="text-on-surface-variant">
                  {flight.departure_local} — {flight.arrival_local}
                </span>
              </li>
            ))}
          </ul>

          <p className="mt-4 text-xs leading-5 text-on-surface-variant">
            Saved to your account and queued for monitoring. Extraction and persistence are
            separate server steps, so incomplete bookings never create partial trips.
          </p>
        </section>
      )}
    </article>
  )
}
