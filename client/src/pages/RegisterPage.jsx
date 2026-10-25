import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import FormField from '../components/FormField'
import { getApiErrorMessage } from '../api/client'
import { useAuth } from '../context/AuthContext'

const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

export default function RegisterPage() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
  })
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

    if (!form.name.trim()) nextErrors.name = 'Enter your name.'
    if (!email) nextErrors.email = 'Enter your email address.'
    else if (!emailPattern.test(email)) nextErrors.email = 'Enter a valid email address.'
    if (!form.password) nextErrors.password = 'Create a password.'
    else if (form.password.length < 8) nextErrors.password = 'Use at least 8 characters.'
    if (!form.confirmPassword) nextErrors.confirmPassword = 'Confirm your password.'
    else if (form.confirmPassword !== form.password) {
      nextErrors.confirmPassword = 'The passwords do not match.'
    }

    setErrors(nextErrors)
    return Object.keys(nextErrors).length === 0
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setServerError('')
    if (!validate()) return

    setSubmitting(true)
    try {
      await register({
        name: form.name.trim(),
        email: form.email.trim(),
        password: form.password,
      })
      navigate('/', { replace: true })
    } catch (error) {
      setServerError(
        getApiErrorMessage(error, 'We could not create your account. Please try again.'),
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
            Make risk easier to manage.
          </h1>
          <p className="mt-5 max-w-lg text-base leading-7 text-emerald-100/80">
            Create a merchant account to view payment activity and review flagged transactions.
          </p>
        </div>
        <p className="text-sm text-emerald-200/70">Fraud Detection Dashboard</p>
      </section>

      <section className="flex items-center justify-center bg-slate-50 px-5 py-12 sm:px-8">
        <div className="w-full max-w-md">
          <p className="text-sm font-semibold text-emerald-700">Get started</p>
          <h2 className="mt-2 text-3xl font-bold tracking-tight text-slate-950">
            Create your account
          </h2>
          <p className="mt-2 text-sm text-slate-600">
            Use your details to set up dashboard access.
          </p>

          <form className="mt-8 space-y-4" noValidate onSubmit={handleSubmit}>
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
              autoComplete="name"
              error={errors.name}
              id="name"
              label="Full name"
              onChange={updateField}
              placeholder="Your name"
              value={form.name}
            />
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
              autoComplete="new-password"
              error={errors.password}
              id="password"
              label="Password"
              minLength={8}
              onChange={updateField}
              placeholder="At least 8 characters"
              type="password"
              value={form.password}
            />
            <FormField
              autoComplete="new-password"
              error={errors.confirmPassword}
              id="confirmPassword"
              label="Confirm password"
              onChange={updateField}
              placeholder="Enter your password again"
              type="password"
              value={form.confirmPassword}
            />
            <button
              className="flex w-full items-center justify-center rounded-xl bg-emerald-700 px-4 py-3 text-sm font-bold text-white transition hover:bg-emerald-800 disabled:cursor-not-allowed disabled:opacity-60"
              disabled={submitting}
              type="submit"
            >
              {submitting ? 'Creating account...' : 'Create account'}
            </button>
          </form>

          <p className="mt-6 text-sm text-slate-600">
            Already registered?{' '}
            <Link className="font-semibold text-emerald-800 hover:underline" to="/login">
              Sign in
            </Link>
          </p>
        </div>
      </section>
    </main>
  )
}
