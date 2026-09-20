import type { StyleSpecification } from 'maplibre-gl'

export const hotelMapStyle: StyleSpecification = {
  version: 8,
  sources: {
    openstreetmap: {
      type: 'raster',
      tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
      tileSize: 256,
      attribution: '© OpenStreetMap contributors',
    },
  },
  layers: [{ id: 'openstreetmap', type: 'raster', source: 'openstreetmap' }],
}

export function hotelSearchUrl(hotel: { name: string; address: string | null; city: string }) {
  const query = [hotel.name, hotel.address, hotel.city].filter(Boolean).join(', ')
  return `https://www.openstreetmap.org/search?query=${encodeURIComponent(query)}`
}

