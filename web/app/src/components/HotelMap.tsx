import { useEffect, useRef, useState } from 'react'
import * as maplibregl from 'maplibre-gl'
import type { Hotel } from '../types'
import { hotelMapStyle, hotelSearchUrl } from '../lib/hotelMap'

export function HotelMap({ hotel }: { hotel: Hotel }) {
  const container = useRef<HTMLDivElement>(null)
  const [failed, setFailed] = useState(false)
  const hasCoordinates = hotel.latitude != null && hotel.longitude != null
  const searchUrl = hotelSearchUrl(hotel)

  useEffect(() => {
    if (!container.current || !hasCoordinates) return
    let map: maplibregl.Map | undefined
    try {
      map = new maplibregl.Map({
        container: container.current,
        style: hotelMapStyle,
        center: [hotel.longitude!, hotel.latitude!],
        zoom: 14,
        cooperativeGestures: true,
        attributionControl: { compact: true },
      })
      map.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-right')
      new maplibregl.Marker({ color: '#0ea5e9' })
        .setLngLat([hotel.longitude!, hotel.latitude!])
        .addTo(map)
    } catch {
      queueMicrotask(() => setFailed(true))
    }
    return () => map?.remove()
  }, [hasCoordinates, hotel.latitude, hotel.longitude])

  if (!hasCoordinates || failed) {
    return (
      <div className="hotel-map hotel-map-fallback">
        <span aria-hidden="true">⌖</span>
        <p>{failed ? 'Interactive map unavailable.' : 'Exact location not found yet.'}</p>
        <a href={searchUrl} rel="noreferrer" target="_blank">Find on OpenStreetMap</a>
      </div>
    )
  }

  return (
    <div className="hotel-map-wrap">
      <div
        aria-label={`Interactive map showing ${hotel.name} in ${hotel.city}`}
        className="hotel-map"
        ref={container}
        role="region"
      />
      <a className="hotel-map-link" href={searchUrl} rel="noreferrer" target="_blank">
        Open larger map ↗
      </a>
    </div>
  )
}
