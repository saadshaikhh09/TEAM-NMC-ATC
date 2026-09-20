export const formatInr = new Intl.NumberFormat('en-IN', {
  style: 'currency',
  currency: 'INR',
  maximumFractionDigits: 0,
}).format

export function formatUtc(value: string) {
  return new Intl.DateTimeFormat('en-GB', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
    timeZone: 'UTC',
    timeZoneName: 'short',
  }).format(new Date(value))
}

/**
 * Money that the API may omit. Null means "not set", never zero — several
 * Constraints and Hotel fields are nullable server-side, and rendering a missing
 * ceiling as ₹0 would state the opposite of what it means.
 */
export function formatInrOrNone(amountInr: number | null, fallback = 'None set') {
  return amountInr === null ? fallback : formatInr(amountInr)
}

/** Departure-board time: 24h, UTC, no date. For option rows where the day is already stated. */
export function formatClock(value: string) {
  return new Intl.DateTimeFormat('en-GB', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
    timeZone: 'UTC',
  }).format(new Date(value))
}

/** Elapsed time between two ISO timestamps, as "9h 55m". Empty string if either is unparseable. */
export function formatDuration(from: string, to: string) {
  const minutes = Math.round((Date.parse(to) - Date.parse(from)) / 60_000)
  if (!Number.isFinite(minutes) || minutes < 0) return ''
  return `${Math.floor(minutes / 60)}h ${String(minutes % 60).padStart(2, '0')}m`
}

/**
 * Signed money, for cost deltas where the sign carries the meaning.
 *
 * Null is handled here rather than at each call site: the API returns null for
 * a delta it never calculated, and `−₹0` would announce "no cost change" for a
 * figure nobody worked out.
 */
export function formatDelta(amountInr: number | null, fallback = 'Not calculated') {
  if (amountInr === null) return fallback
  if (amountInr === 0) return 'No change'
  return `${amountInr > 0 ? '+' : '−'}${formatInr(Math.abs(amountInr))}`
}
