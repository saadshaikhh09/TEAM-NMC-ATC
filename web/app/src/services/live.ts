/**
 * WS /ws subscription with deterministic backoff and a REST polling fallback.
 *
 * Three rules this file exists to enforce:
 *   1. Switch on `type` only. The eight names in CONTRACT.md are fixed strings;
 *      an unrecognised envelope is dropped here and never reaches the UI.
 *   2. A dropped socket never blanks the screen and never throws into render.
 *      Every callback is fired outside the render tree; the caller keeps its
 *      last known state until a refetch succeeds.
 *   3. Nothing is random. The backoff ladder is a fixed table so thirty
 *      rehearsals behave identically.
 *
 * The polling fallback targets our own FastAPI only. The 500/month quota rules
 * apply to live status providers, which the browser never touches.
 */
import type { WsEvent, WsEventType } from '../types'
import { apiBase } from './api'

export type LiveStatus = 'connecting' | 'live' | 'reconnecting' | 'polling'

/** CONTRACT.md — frozen. Do not alias, normalise or extend. */
const EVENT_TYPES: ReadonlySet<string> = new Set<WsEventType>([
  'trip.updated',
  'disruption.detected',
  'plan.ready',
  'plan.awaiting_approval',
  'plan.executing',
  'plan.executed',
  'plan.failed',
  'action.recorded',
])

const BACKOFF_MS = [500, 1000, 2000, 4000, 8000] as const
/** Failed attempts before we stop waiting on the socket and poll REST instead. */
const POLL_AFTER_ATTEMPTS = 3
const POLL_INTERVAL_MS = 4000

export function websocketUrl(): string {
  if (apiBase) return `${apiBase.replace(/^http/, 'ws')}/ws`
  const scheme = window.location.protocol === 'https:' ? 'wss' : 'ws'
  return `${scheme}://${window.location.host}/ws`
}

/** Returns the event only if it is a well-formed envelope with a known type. */
export function parseEvent(raw: unknown): WsEvent | null {
  if (typeof raw !== 'string') return null
  let decoded: unknown
  try {
    decoded = JSON.parse(raw)
  } catch {
    return null
  }
  if (typeof decoded !== 'object' || decoded === null) return null
  const { type, trip_id: tripId, payload } = decoded as Record<string, unknown>
  if (typeof type !== 'string' || !EVENT_TYPES.has(type)) return null
  if (typeof tripId !== 'string') return null
  return {
    type: type as WsEventType,
    trip_id: tripId,
    payload: (typeof payload === 'object' && payload !== null ? payload : {}) as Record<string, unknown>,
  }
}

interface LiveOptions {
  onEvent: (event: WsEvent) => void
  onStatus: (status: LiveStatus) => void
  /** Called on each polling tick once the socket is judged unavailable. */
  onPoll: () => void
}

/** Opens the socket and returns a disposer. Never throws. */
export function connectLive({ onEvent, onStatus, onPoll }: LiveOptions): () => void {
  let socket: WebSocket | null = null
  let attempt = 0
  let reconnectTimer = 0
  let pollTimer = 0
  let disposed = false

  const stopPolling = () => {
    if (!pollTimer) return
    window.clearInterval(pollTimer)
    pollTimer = 0
  }

  const startPolling = () => {
    if (pollTimer || disposed) return
    onStatus('polling')
    onPoll()
    pollTimer = window.setInterval(onPoll, POLL_INTERVAL_MS)
  }

  const scheduleReconnect = () => {
    if (disposed) return
    if (attempt >= POLL_AFTER_ATTEMPTS) startPolling()
    else onStatus('reconnecting')
    const delay = BACKOFF_MS[Math.min(attempt, BACKOFF_MS.length - 1)]
    attempt += 1
    reconnectTimer = window.setTimeout(open, delay)
  }

  function open() {
    if (disposed) return
    let next: WebSocket
    try {
      next = new WebSocket(websocketUrl())
    } catch {
      scheduleReconnect()
      return
    }
    socket = next

    next.onopen = () => {
      attempt = 0
      stopPolling()
      onStatus('live')
    }
    next.onmessage = (message: MessageEvent) => {
      const event = parseEvent(message.data)
      if (event) onEvent(event)
    }
    // An errored socket always emits close afterwards; reconnect is handled there.
    next.onerror = () => {}
    next.onclose = () => {
      if (socket === next) socket = null
      scheduleReconnect()
    }
  }

  onStatus('connecting')
  open()

  return () => {
    disposed = true
    window.clearTimeout(reconnectTimer)
    stopPolling()
    if (socket) {
      socket.onclose = null
      socket.close()
      socket = null
    }
  }
}
