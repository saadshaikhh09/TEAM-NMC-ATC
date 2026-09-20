import assert from 'node:assert/strict'
import { mkdir } from 'node:fs/promises'
import { resolve } from 'node:path'
import { chromium, request } from 'playwright-core'

const site = process.env.QA_SITE_URL ?? 'http://localhost:5173'
const app = process.env.QA_APP_URL ?? 'http://localhost:5174'
const api = process.env.QA_API_URL ?? 'http://127.0.0.1:8000'
const output = resolve('../../tmp/browser-qa')
await mkdir(output, { recursive: true })
const browser = await chromium.launch({
  headless: true,
  ...(process.env.QA_BROWSER_CHANNEL ? { channel: process.env.QA_BROWSER_CHANNEL } : {}),
})
const failures = []
const report = (label, value) => console.log(`${label}: ${value}`)

async function overflow(page, label) {
  const result = await page.evaluate(() => ({
    width: document.documentElement.clientWidth,
    scrollWidth: document.documentElement.scrollWidth,
    offenders: [...document.querySelectorAll('body *')]
      .filter((node) => {
        const rect = node.getBoundingClientRect()
        return rect.left < -1 || rect.right > document.documentElement.clientWidth + 1
      })
      .slice(0, 5).map((node) => `${node.tagName.toLowerCase()}.${String(node.className).split(' ')[0]}`),
  }))
  if (result.width !== result.scrollWidth) failures.push(`${label}: ${JSON.stringify(result)}`)
}

try {
  const page = await browser.newPage()
  page.on('pageerror', (error) => { failures.push(`Public JS: ${error.message}`); console.error('Public JS:', error.message) })
  page.on('console', (message) => { if (message.type() === 'error') failures.push(`Public console: ${message.text()}`) })
  page.on('requestfailed', (request) => { if (request.url().startsWith(site) && request.failure()?.errorText !== 'net::ERR_ABORTED') failures.push(`Public request: ${request.url()} ${request.failure()?.errorText}`) })
  for (const width of [320, 375, 390, 768, 1024, 1280, 1440]) {
    await page.setViewportSize({ width, height: 900 })
    for (const route of ['/', '/how-it-works', '/faq', '/missing-route']) {
      report('Checking', `Public ${route} at ${width}px`)
      const response = await page.goto(`${site}${route}`, { waitUntil: 'domcontentloaded' })
      assert.equal(response.status(), 200)
      await page.locator('h1').first().waitFor()
      await page.evaluate(() => document.fonts.ready)
      await overflow(page, `Public ${route} at ${width}px`)
    }
  }
  report('Public routes and widths', '4 routes × 7 widths checked')

  await page.setViewportSize({ width: 1280, height: 900 })
  await page.goto(`${site}/how-it-works`)
  await page.evaluate(() => window.scrollTo(0, 0))
  await page.waitForTimeout(50)
  const start = await page.locator('.progress-line').evaluate((node) => getComputedStyle(node).transform)
  await page.evaluate(() => window.scrollTo(0, document.documentElement.scrollHeight))
  await page.waitForTimeout(50)
  const end = await page.locator('.progress-line').evaluate((node) => getComputedStyle(node).transform)
  assert.match(start, /^matrix\(0, 0, 0, 1, 0, 0\)$/)
  assert.match(end, /^matrix\(1, 0, 0, 1, 0, 0\)$/)
  const sticky = await page.locator('.stage-card').first().evaluate((node) => getComputedStyle(node).position)
  assert.equal(sticky, 'sticky')
  await page.emulateMedia({ reducedMotion: 'reduce' })
  const natural = await page.locator('.stage-card').first().evaluate((node) => getComputedStyle(node).position)
  assert.equal(natural, 'relative')
  await page.emulateMedia({ reducedMotion: 'no-preference' })
  await page.setViewportSize({ width: 390, height: 720 })
  const mobile = await page.locator('.stage-card').first().evaluate((node) => getComputedStyle(node).position)
  assert.equal(mobile, 'relative')
  report('Progress and stacked cards', '0% → 100%; sticky desktop; natural reduced-motion/mobile')

  await page.goto(site)
  await page.evaluate(() => window.scrollTo(0, document.documentElement.scrollHeight))
  await page.waitForTimeout(400)
  assert.equal(await page.locator('.reveal-on-scroll[data-visible="false"]').count(), 0)
  await page.evaluate(() => window.scrollTo(0, 0))
  await page.screenshot({ path: resolve(output, 'site-mobile.png'), fullPage: true })
  await page.setViewportSize({ width: 1440, height: 900 })
  await page.goto(site)
  await page.evaluate(() => window.scrollTo(0, document.documentElement.scrollHeight))
  await page.waitForTimeout(400)
  assert.equal(await page.locator('.reveal-on-scroll[data-visible="false"]').count(), 0)
  await page.evaluate(() => window.scrollTo(0, 0))
  await page.screenshot({ path: resolve(output, 'site-desktop.png'), fullPage: true })
  assert.equal(await page.locator('a[href$="/signup"]').count() > 0, true)

  const privatePage = await browser.newPage({ viewport: { width: 390, height: 844 } })
  privatePage.on('pageerror', (error) => failures.push(`App JS: ${error.message}`))
  privatePage.on('console', (message) => {
    const location = message.location().url
    const pendingPlan = message.text().includes('404 (Not Found)') && /\/disruptions\/[^/]+\/plan$/.test(location)
    if (message.type() === 'error' && !message.text().includes('401 (Unauthorized)') && !pendingPlan) {
      failures.push(`App console: ${message.text()} ${message.location().url}`)
    }
  })
  privatePage.on('requestfailed', (request) => { if (request.url().startsWith(app) && request.failure()?.errorText !== 'net::ERR_ABORTED') failures.push(`App request: ${request.url()} ${request.failure()?.errorText}`) })
  await privatePage.goto(`${app}/app/trips/new`)
  await privatePage.waitForURL('**/login')
  await privatePage.goto(`${app}/signup`)
  await privatePage.getByLabel('Full name').fill('Browser QA')
  await privatePage.getByLabel('Email address').fill(`browser-qa-${Date.now()}@example.test`)
  await privatePage.getByLabel('Password').fill('StrongPass!2026')
  await privatePage.getByRole('button', { name: 'Create account' }).click()
  await privatePage.waitForURL('**/app')
  await privatePage.goto(`${app}/app/trips/new`)
  const travellerHeight = await privatePage.locator('[name="traveller_name"]').evaluate((node) => node.getBoundingClientRect().height)
  const cabinHeight = await privatePage.locator('[name="cabin"]').evaluate((node) => node.getBoundingClientRect().height)
  assert.equal(cabinHeight, travellerHeight)
  assert.equal(await privatePage.locator('.mobile-nav').evaluate((node) => getComputedStyle(node).position), 'sticky')
  const mobileNavBox = await privatePage.locator('.mobile-nav').boundingBox()
  const mainBox = await privatePage.locator('#app-main').boundingBox()
  assert.equal(Boolean(mobileNavBox && mainBox && mobileNavBox.y + mobileNavBox.height <= mainBox.y + 1), true)
  await privatePage.screenshot({ path: resolve(output, 'app-new-trip-mobile.png'), fullPage: true })
  await privatePage.locator('[name="traveller_name"]').fill('Browser QA')
  await privatePage.locator('[name="carrier"]').fill('AI')
  await privatePage.locator('[name="origin"]').fill('BOM')
  await privatePage.locator('[name="destination"]').fill('LHR')
  await privatePage.locator('[name="flight_number"]').fill('AI909')
  await privatePage.locator('[name="departure"]').fill('2026-10-01T10:00')
  await privatePage.locator('[name="arrival"]').fill('2026-10-01T15:30')
  await privatePage.locator('[name="fare_inr"]').fill('42000')
  await privatePage.getByRole('button', { name: 'Save and monitor' }).click()
  await privatePage.waitForURL(/\/app\/trips\/[0-9a-f-]+$/)
  const tripPath = new URL(privatePage.url()).pathname
  await privatePage.reload()
  assert.equal(new URL(privatePage.url()).pathname, tripPath)
  await privatePage.goto(`${app}${tripPath}/recovery`)
  await privatePage.getByRole('button', { name: 'Simulate cancellation' }).click()
  await privatePage.getByText('Review decision').waitFor()
  await privatePage.getByRole('button', { name: 'Review decision' }).click()
  await privatePage.getByRole('button', { name: 'Approve recovery' }).click()
  await privatePage.getByRole('heading', { name: 'Trip recovered.' }).waitFor()
  await privatePage.getByRole('heading', { name: 'Agent timeline' }).waitFor()
  await privatePage.screenshot({ path: resolve(output, 'app-recovery-mobile.png'), fullPage: true })
  await privatePage.setViewportSize({ width: 1440, height: 900 })
  await privatePage.screenshot({ path: resolve(output, 'app-recovery-desktop.png'), fullPage: true })
  report('Authenticated flow', 'guard → signup → create → refresh → simulate → approve → executed')

  for (const width of [320, 390, 768, 1280]) {
    await privatePage.setViewportSize({ width, height: 900 })
    for (const route of ['/app', '/app/trips', '/app/trips/new', tripPath, `${tripPath}/recovery`, '/app/profile', '/app/unknown']) {
      await privatePage.goto(`${app}${route}`)
      await privatePage.locator('h1').first().waitFor()
      await overflow(privatePage, `App ${route} at ${width}px`)
      await privatePage.waitForTimeout(100)
      await overflow(privatePage, `App settled ${route} at ${width}px`)
    }
  }
  await privatePage.goto(app)
  await privatePage.screenshot({ path: resolve(output, 'app-mobile.png'), fullPage: true })
  report('App routes and widths', '7 routes × 4 widths checked')

  const mapPage = await browser.newPage({ viewport: { width: 1440, height: 900 } })
  await mapPage.goto(`${app}/login`)
  await mapPage.getByLabel('Email address').fill('demo@atc.local')
  await mapPage.getByLabel('Password').fill('DemoPass!2026')
  await mapPage.getByRole('button', { name: 'Log in' }).click()
  await mapPage.waitForURL('**/app')
  await mapPage.goto(`${app}/app/trips/aaaaaaaa-1111-1111-1111-111111111111`)
  await mapPage.locator('.maplibregl-canvas').waitFor()
  assert.match(await mapPage.locator('.maplibregl-ctrl-attrib').textContent(), /OpenStreetMap/)
  await mapPage.screenshot({ path: resolve(output, 'app-hotel-map-desktop.png'), fullPage: true })
  await mapPage.setViewportSize({ width: 390, height: 844 })
  await mapPage.screenshot({ path: resolve(output, 'app-hotel-map-mobile.png'), fullPage: true })
  await mapPage.close()
  report('Hotel map', 'seeded coordinates → MapLibre canvas + OpenStreetMap attribution')

  const owner = await request.newContext({ baseURL: api })
  const other = await request.newContext({ baseURL: api })
  assert.equal((await owner.get('/health')).status(), 200)
  const stamp = Date.now()
  assert.equal((await owner.post('/auth/register', { data: { name: 'Smoke Owner', email: `smoke-owner-${stamp}@example.test`, password: 'StrongPass!2026' } })).status(), 201)
  assert.equal((await other.post('/auth/register', { data: { name: 'Smoke Other', email: `smoke-other-${stamp}@example.test`, password: 'StrongPass!2026' } })).status(), 201)
  const created = await owner.post('/trips', { data: { traveller_name: 'Smoke Owner', origin: 'JFK', destination: 'NRT', outbound: { carrier: 'AT', flight_number: 'AT101', origin: 'JFK', destination: 'NRT', origin_timezone: 'America/New_York', destination_timezone: 'Asia/Tokyo', scheduled_departure: '2026-10-05T10:00:00-04:00', scheduled_arrival: '2026-10-06T14:00:00+09:00' } } })
  assert.equal(created.status(), 201)
  const id = (await created.json()).id
  assert.equal((await other.get(`/trips/${id}`)).status(), 404)
  assert.equal((await owner.post('/auth/logout')).status(), 204)
  assert.equal((await owner.get(`/trips/${id}`)).status(), 401)
  report('API smoke', 'health; two accounts; trip persistence; cross-account 404; logout 401')
  await owner.dispose(); await other.dispose()
} finally {
  await browser.close()
}

if (failures.length) {
  throw new Error(failures.join('\n'))
}
report('Browser QA', 'PASS')
