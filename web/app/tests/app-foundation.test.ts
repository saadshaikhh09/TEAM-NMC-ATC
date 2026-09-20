import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import test from 'node:test'
import { createRequestGate } from '../src/lib/requestGate.ts'

test('stale responses cannot replace the newest route data', () => {
  const gate = createRequestGate()
  const oldRequest = gate.next()
  const newestRequest = gate.next()
  assert.equal(gate.isCurrent(oldRequest), false)
  assert.equal(gate.isCurrent(newestRequest), true)
  gate.cancel()
  assert.equal(gate.isCurrent(newestRequest), false)
})

test('all required authenticated routes are declared', () => {
  const source = readFileSync(new URL('../src/App.tsx', import.meta.url), 'utf8')
  for (const route of ['trips', 'trips/new', 'trips/:tripId', 'trips/:tripId/recovery', 'profile']) {
    assert.match(source, new RegExp(`path=\\"${route.replaceAll('/', '\\/')}\\"`))
  }
  assert.match(source, /<ProtectedShell/)
  assert.match(source, /path="\*" element={<AppNotFound/)
})
