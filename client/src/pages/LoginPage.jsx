import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import FormField from '../components/FormField'
import { getApiErrorMessage } from '../api/client'
import { useAuth } from '../context/AuthContext'

const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

export default function LoginPage() {
  const { login } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', password: '' })
  const [errors, setErrors] = useState({})
  const [serverError, setServerError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  function updateField(event) {
    const { name, value } = event.target
    setForm((current) => ({ ...current, [name]: value }))
    setErrors((current) => ({ ...current, [name]: '' }))
    setServerError('')
  }

  function validate() {
    const nextErrors = {}
    const email = form.email.trim()

    if (!email) nextErrors.email = 'Enter your email address.'
    else if (!emailPattern.test(email)) nextErrors.email = 'Enter a valid email address.'
    if (!form.password) nextErrors.password = 'Enter your password.'

    setErrors(nextErrors)
    return Object.keys(nextErrors).length === 0
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setServerError('')
    if (!validate()) return

    setSubmitting(true)
    try {
      await login({ email: form.email.trim(), password: form.password })
      const destination = location.state?.from?.pathname || '/'
      navigate(destination, { replace: true })
    } catch (error) {
      setServerError(
        getApiErrorMessage(error, 'We could not sign you in. Check your details and try again.'),
      )
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="grid min-h-screen bg-slate-950 lg:grid-cols-[1.05fr_0.95fr]">
      <section className="hidden flex-col justify-between bg-emerald-950 p-12 text-white lg:flex">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.2em] text-emerald-300">
            Payment risk console
          </p>
          <h1 className="mt-16 max-w-xl text-5xl font-bold leading-tight tracking-tight">
            See payment risk clearly.
          </h1>
          <p className="mt-5 max-w-lg text-base leading-7 text-emerald-100/80">
            Review transactions, understand risk signals, and make confident decisions from one
            dashboard.
          </p>
        </div>
        <p className="text-sm text-emerald-200/70">Fraud Detection Dashboard</p>
      </section>

      <section className="flex items-center justify-center bg-slate-50 px-5 py-12 sm:px-8">
        <div className="w-full max-w-md">
          <p className="text-sm font-semibold text-emerald-700">Welcome back</p>
          <h2 className="mt-2 text-3xl font-bold tracking-tight text-slate-950">Sign in</h2>
          <p className="mt-2 text-sm text-slate-600">
            Enter your account details to open the dashboard.
          </p>

          <form className="mt-8 space-y-5" noValidate onSubmit={handleSubmit}>
            {serverError && (
              <p
                aria-live="polite"
                className="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800"
                role="alert"
              >
                {serverError}
              </p>
            )}
            <FormField
              autoComplete="email"
              error={errors.email}
              id="email"
              label="Email address"
              onChange={updateField}
              placeholder="you@example.com"
              type="email"
              value={form.email}
            />
            <FormField
              autoComplete="current-password"
              error={errors.password}
              id="password"
              label="Password"
              onChange={updateField}
              placeholder="Your password"
              type="password"
              value={form.password}
            />
            <button
              className="flex w-full items-center justify-center rounded-xl bg-emerald-700 px-4 py-3 text-sm font-bold text-white transition hover:bg-emerald-800 disabled:cursor-not-allowed disabled:opacity-60"
              disabled={submitting}
              type="submit"
            >
              {submitting ? 'Signing in...' : 'Sign in'}
            </button>
          </form>

          <p className="mt-6 text-sm text-slate-600">
            New to the dashboard?{' '}
            <Link className="font-semibold text-emerald-800 hover:underline" to="/register">
              Create an account
            </Link>
          </p>
        </div>
      </section>
    </main>
  )
}
