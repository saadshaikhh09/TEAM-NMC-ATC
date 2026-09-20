import assert from 'node:assert/strict'
import test from 'node:test'

test('hotel map config preserves OpenStreetMap attribution and an encoded fallback', async () => {
  const { hotelMapStyle, hotelSearchUrl } = await import('../src/lib/hotelMap.ts')

  assert.equal(
    hotelSearchUrl({ name: 'Hôtel & Spa', address: null, city: 'Paris' }),
    'https://www.openstreetmap.org/search?query=H%C3%B4tel%20%26%20Spa%2C%20Paris',
  )
  assert.deepEqual(hotelMapStyle.sources.openstreetmap, {
    type: 'raster',
    tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
    tileSize: 256,
    attribution: '© OpenStreetMap contributors',
  })
})
