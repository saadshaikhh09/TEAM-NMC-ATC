function value(data: FormData, name: string) {
  return String(data.get(name) ?? '').trim()
}

export function hotelFromForm(data: FormData) {
  const name = value(data, 'hotel_name')
  if (!name) return null
  return {
    name,
    address: value(data, 'hotel_address') || null,
    city: value(data, 'hotel_city'),
    city_timezone: value(data, 'hotel_timezone') || null,
    check_in: value(data, 'hotel_check_in'),
    check_out: value(data, 'hotel_check_out'),
    confirmation_number: value(data, 'hotel_confirmation') || null,
    nightly_rate_inr: value(data, 'hotel_rate') ? Number(value(data, 'hotel_rate')) : null,
    modifiable: data.has('hotel_modifiable'),
  }
}

