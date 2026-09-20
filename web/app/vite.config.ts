import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

const api = 'http://localhost:8000'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5174,
    strictPort: true,
    // Same-origin in dev, so REST and WS need no backend CORS entry for :5174.
    // Set VITE_API_URL to point a built bundle at an API on another origin.
    proxy: {
      '/trips': api,
      '/approvals': api,
      '/disruptions': api,
      '/simulate': api,
      '/health': api,
      '/auth': api,
      '/profile': api,
      '/ws': { target: api.replace(/^http/, 'ws'), ws: true },
    },
  },
})
