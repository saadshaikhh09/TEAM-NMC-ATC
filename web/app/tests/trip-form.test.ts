import assert from 'node:assert/strict'
import test from 'node:test'

test('hotel form payload preserves address and flexible-rate choice', async () => {
  const { hotelFromForm } = await import('../src/lib/tripForm.ts')
  const data = new FormData()
  data.set('hotel_name', 'Kensington Central')
  data.set('hotel_address', 'Scarsdale Place')
  data.set('hotel_city', 'LON')
  data.set('hotel_check_in', '2026-10-01')
  data.set('hotel_check_out', '2026-10-03')

  assert.equal(hotelFromForm(data)?.modifiable, false)
  data.set('hotel_modifiable', 'on')
  assert.deepEqual(hotelFromForm(data), {
    name: 'Kensington Central',
    address: 'Scarsdale Place',
    city: 'LON',
    city_timezone: null,
    check_in: '2026-10-01',
    check_out: '2026-10-03',
    confirmation_number: null,
    nightly_rate_inr: null,
    modifiable: true,
  })
})
