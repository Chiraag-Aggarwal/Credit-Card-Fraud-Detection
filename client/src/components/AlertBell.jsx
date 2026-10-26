import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import apiClient from '../api/client'

export default function AlertBell() {
  const [count, setCount] = useState(0)

  useEffect(() => {
    let active = true

    async function loadUnreadCount() {
      try {
        const { data } = await apiClient.get('/api/alerts/unread-count')
        if (active) setCount(Number.isFinite(data.count) ? Math.max(0, data.count) : 0)
      } catch {
        if (active) setCount(0)
      }
    }

    void loadUnreadCount()
    const intervalId = window.setInterval(loadUnreadCount, 15000)

    return () => {
      active = false
      window.clearInterval(intervalId)
    }
  }, [])

  const label =
    count > 0 ? 'Flagged transactions, ' + count + ' unread' : 'Flagged transactions'

  return (
    <Link
      aria-label={label}
      className="relative grid h-10 w-10 place-items-center rounded-lg text-slate-600 transition hover:bg-slate-100 hover:text-slate-900"
      title={label}
      to="/flagged"
    >
      <svg
        aria-hidden="true"
        className="h-5 w-5"
        fill="none"
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="1.8"
        viewBox="0 0 24 24"
      >
        <path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9" />
        <path d="M10 21h4" />
      </svg>
      {count > 0 && (
        <span
          aria-hidden="true"
          className="absolute -right-1 -top-1 grid min-h-5 min-w-5 place-items-center rounded-full bg-rose-600 px-1 text-[10px] font-bold leading-none text-white ring-2 ring-white"
        >
          {count}
        </span>
      )}
    </Link>
  )
}
