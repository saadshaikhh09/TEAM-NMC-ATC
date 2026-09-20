export const appBase = (import.meta.env.VITE_APP_URL ?? 'http://localhost:5174').replace(/\/$/, '')
export const appLink = (path: string) => `${appBase}${path.startsWith('/') ? path : `/${path}`}`
