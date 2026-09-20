import { useEffect, useState, type FormEvent } from 'react'
import { Link, Navigate, Outlet, Route, Routes, useLocation, useNavigate } from 'react-router-dom'
import { AppShell } from './components/AppShell'
import { AUTH_EXPIRED_EVENT, authApi, type Account } from './services/api'
import { AppNotFound, NewTripPage, OverviewPage, ProfilePage, RecoveryPage, TripDetailPage, TripsPage } from './screens/Pages'

function AuthPage({ mode, onAuthenticated }: { mode: 'login' | 'signup'; onAuthenticated: (account: Account) => void }) {
  const navigate = useNavigate()
  const location = useLocation()
  const [error, setError] = useState<string | null>(null)
  const [pending, setPending] = useState(false)
  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault(); setPending(true); setError(null)
    const data = new FormData(event.currentTarget)
    try {
      const account = mode === 'login'
        ? await authApi.login(String(data.get('email')), String(data.get('password')))
        : await authApi.register(String(data.get('name')), String(data.get('email')), String(data.get('password')))
      onAuthenticated(account)
      const from = (location.state as { from?: string } | null)?.from
      navigate(from?.startsWith('/app') ? from : '/app', { replace: true })
    } catch (cause) { setError(cause instanceof Error ? cause.message : 'Authentication failed.') } finally { setPending(false) }
  }
  const title = mode === 'login' ? 'Welcome back.' : 'Your concierge starts here.'
  return (
    <main className="app-theme auth-page">
      <section className="auth-visual" aria-label="ATC route radar">
        <a className="auth-brand" href={import.meta.env.VITE_SITE_URL ?? 'http://localhost:5173'}><img alt="ATC" src="/assets/atc-logo.png" /></a>
        <div className="auth-radar" aria-hidden="true"><span /><span /><span /></div>
        <div><p>SIMULATED FEED · REAL DECISION LOGIC</p><h1>Disruption does not have to become disorder.</h1><span>Deterministic recovery, readable from detection to confirmation.</span></div>
      </section>
      <section className="auth-form-wrap">
        <form aria-describedby={error ? 'auth-error' : undefined} className="auth-form" onSubmit={(event) => void submit(event)}>
          <p className="auth-eyebrow">ATC MEMBER PORTAL</p><h2>{title}</h2><p>{mode === 'login' ? 'Open your private trip workspace.' : 'Create a secure account and add your first itinerary.'}</p>
          {mode === 'signup' && <label>Full name<input autoComplete="name" name="name" required /></label>}
          <label>Email address<input autoComplete="email" name="email" required type="email" /></label>
          <label>Password<input aria-describedby={mode === 'signup' ? 'password-help' : undefined} autoComplete={mode === 'login' ? 'current-password' : 'new-password'} minLength={12} name="password" required type="password" /></label>
          {mode === 'signup' && <small id="password-help">At least 12 characters with uppercase, lowercase, number and symbol.</small>}
          <p className="form-error" id="auth-error" role={error ? 'alert' : undefined}>{error}</p>
          <button disabled={pending} type="submit">{pending ? 'Please wait…' : mode === 'login' ? 'Log in' : 'Create account'}</button>
          <p className="auth-switch">{mode === 'login' ? <>New to ATC? <Link to="/signup">Create an account</Link></> : <>Already registered? <Link to="/login">Log in</Link></>}</p>
          <p className="auth-boundary">HttpOnly sessions · No tokens in browser storage</p>
        </form>
      </section>
    </main>
  )
}

function ProtectedShell({ account, logout }: { account: Account | null; logout: () => Promise<void> }) {
  const location = useLocation()
  if (!account) return <Navigate replace state={{ from: location.pathname }} to="/login" />
  return <AppShell account={account} onLogout={logout}><Outlet /></AppShell>
}

export default function App() {
  const [account, setAccount] = useState<Account | null | undefined>(undefined)
  const navigate = useNavigate()
  useEffect(() => { void authApi.session().then(setAccount, () => setAccount(null)) }, [])
  useEffect(() => {
    const expire = () => { setAccount(null); navigate('/login', { replace: true }) }
    window.addEventListener(AUTH_EXPIRED_EVENT, expire)
    return () => window.removeEventListener(AUTH_EXPIRED_EVENT, expire)
  }, [navigate])
  const logout = async () => { await authApi.logout(); setAccount(null); navigate('/login', { replace: true }) }
  if (account === undefined) return <main className="session-loading" aria-busy="true"><img alt="ATC" src="/assets/atc-logo.png" /><span>Opening your secure session…</span></main>
  return (
    <Routes>
      <Route path="/login" element={account ? <Navigate replace to="/app" /> : <AuthPage mode="login" onAuthenticated={setAccount} />} />
      <Route path="/signup" element={account ? <Navigate replace to="/app" /> : <AuthPage mode="signup" onAuthenticated={setAccount} />} />
      <Route path="/app" element={<ProtectedShell account={account} logout={logout} />}>
        <Route index element={<OverviewPage />} />
        <Route path="trips" element={<TripsPage />} />
        <Route path="trips/new" element={<NewTripPage />} />
        <Route path="trips/:tripId" element={<TripDetailPage />} />
        <Route path="trips/:tripId/recovery" element={<RecoveryPage />} />
        <Route path="profile" element={<ProfilePage account={account!} onLogout={logout} />} />
        <Route path="*" element={<AppNotFound />} />
      </Route>
      <Route path="*" element={account ? <Navigate replace to="/app" /> : <Navigate replace to="/login" />} />
    </Routes>
  )
}
