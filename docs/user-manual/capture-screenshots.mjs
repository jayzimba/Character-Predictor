/**
 * Capture Microsoft Edge screenshots of the live Temperament Lab site
 * for the user manual. Uses the installed Edge browser (channel: msedge).
 *
 *   cd docs/user-manual
 *   npm install playwright-core
 *   node capture-screenshots.mjs
 */
import { mkdir } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { chromium } from 'playwright-core'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const OUT = path.join(__dirname, 'screenshots')
const BASE = process.env.MANUAL_BASE_URL || 'https://pc.zebprojecthub.com'
const USER_EMAIL = process.env.MANUAL_USER_EMAIL || 'user@temperamentlab.local'
const USER_PASSWORD = process.env.MANUAL_USER_PASSWORD || 'DemoUser123!'
const ADMIN_EMAIL = process.env.MANUAL_ADMIN_EMAIL || 'admin@temperamentlab.local'
const ADMIN_PASSWORD = process.env.MANUAL_ADMIN_PASSWORD || 'AdminDemo123!'

async function shot(page, name, { fullPage = false } = {}) {
  const file = path.join(OUT, `${name}.png`)
  await page.waitForTimeout(600)
  await page.screenshot({ path: file, fullPage, animations: 'disabled' })
  console.log('saved', name)
}

async function goto(page, route) {
  await page.goto(`${BASE}${route}`, { waitUntil: 'networkidle', timeout: 45000 })
  await page.waitForTimeout(800)
}

async function signIn(page, email, password) {
  await goto(page, '/login')
  await page.getByLabel('Email').fill(email)
  await page.getByLabel('Password').fill(password)
  await page.getByRole('button', { name: 'Sign in' }).click()
  await page.waitForURL(/\/(app|admin)/, { timeout: 20000 })
  await page.waitForTimeout(1000)
}

async function signOut(page) {
  const button = page.getByRole('button', { name: 'Sign out' })
  if (await button.count()) {
    await button.click()
    await page.waitForURL((url) => url.pathname === '/' || url.pathname === '/login', {
      timeout: 15000,
    }).catch(() => {})
    await page.waitForTimeout(500)
  }
}

async function completeAssessment(page) {
  await goto(page, '/app/assessment')
  const consent = page.getByRole('checkbox')
  if (await consent.count()) {
    await shot(page, '08-assessment-consent')
    await consent.check()
    await page.getByRole('button', { name: 'Start assessment' }).click()
    await page.getByText(/Question \d+ of \d+/).waitFor({ timeout: 20000 })
  }

  const heading = await page.getByText(/Question \d+ of \d+/).textContent()
  const total = Number((heading.match(/of (\d+)/) || [0, '0'])[1])
  await shot(page, '09-assessment-question')

  for (let i = 0; i < total; i += 1) {
    const labels = page.locator('fieldset label')
    const count = await labels.count()
    if (count === 0) break
    // Vary Likert 1–5 so the mix is not a single spike.
    const choice = i % 5
    await labels.nth(choice).click()
    await page.waitForTimeout(120)
    if (i < total - 1) {
      await page.getByRole('button', { name: 'Next' }).click()
      await page.waitForTimeout(80)
    }
  }

  await page.getByRole('button', { name: 'Submit assessment' }).click()
  await page
    .getByRole('heading', { name: /Your assessment indicates|Your answers are stored/ })
    .waitFor({ timeout: 30000 })
  await shot(page, '10-assessment-complete', { fullPage: true })

  const fullResult = page.getByRole('link', { name: 'View full result' })
  if (await fullResult.count()) {
    await fullResult.click()
    await page.waitForURL(/\/app\/results/, { timeout: 15000 })
    await page.waitForTimeout(1200)
    await shot(page, '11-results', { fullPage: true })
  }
}

async function main() {
  await mkdir(OUT, { recursive: true })

  const browser = await chromium.launch({
    channel: 'msedge',
    headless: true,
    args: ['--disable-dev-shm-usage'],
  })
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    deviceScaleFactor: 1,
    userAgent:
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
  })
  const page = await context.newPage()
  page.setDefaultTimeout(25000)

  try {
    await goto(page, '/')
    await shot(page, '01-home')
    await page.evaluate(() => {
      document.getElementById('how-it-works')?.scrollIntoView({ behavior: 'instant', block: 'start' })
    })
    await shot(page, '02-home-how-it-works')
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight))
    await shot(page, '03-home-footer')

    await goto(page, '/personality-types')
    await shot(page, '04-personality-types', { fullPage: true })

    await goto(page, '/about')
    await shot(page, '05-about', { fullPage: true })

    await goto(page, '/register')
    await shot(page, '06-register', { fullPage: true })

    await goto(page, '/login')
    await shot(page, '07-login', { fullPage: true })

    await signIn(page, USER_EMAIL, USER_PASSWORD)
    await goto(page, '/app')
    await shot(page, '07b-user-dashboard-before', { fullPage: true })

    await completeAssessment(page)

    await goto(page, '/app')
    await shot(page, '12-user-dashboard', { fullPage: true })

    await goto(page, '/app/history')
    await shot(page, '13-history', { fullPage: true })

    await goto(page, '/app/profile')
    await shot(page, '14-profile', { fullPage: true })

    await signOut(page)

    await signIn(page, ADMIN_EMAIL, ADMIN_PASSWORD)
    await goto(page, '/admin')
    await shot(page, '15-admin-overview', { fullPage: true })

    await goto(page, '/admin/users')
    await shot(page, '16-admin-users', { fullPage: true })

    await goto(page, '/admin/questions')
    await shot(page, '17-admin-questions', { fullPage: true })

    await goto(page, '/admin/assessments')
    await shot(page, '18-admin-assessments', { fullPage: true })

    await goto(page, '/admin/models')
    await shot(page, '19-admin-models', { fullPage: true })

    await goto(page, '/admin/dataset')
    await shot(page, '20-admin-dataset', { fullPage: true })

    await goto(page, '/admin/training')
    await shot(page, '21-admin-training', { fullPage: true })

    await goto(page, '/admin/analytics')
    await shot(page, '22-admin-analytics', { fullPage: true })

    await goto(page, '/admin/audit')
    await shot(page, '23-admin-audit', { fullPage: true })
  } finally {
    await browser.close()
  }
}

main().catch((error) => {
  console.error(error)
  process.exit(1)
})
