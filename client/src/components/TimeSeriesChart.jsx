import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

function formatTick(value, period) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  return period === '24h'
    ? date.toLocaleTimeString([], { hour: 'numeric' })
    : date.toLocaleDateString([], { month: 'short', day: 'numeric' })
}

function formatLabel(value) {
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString()
}

export default function TimeSeriesChart({ data, period, onPeriodChange }) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-slate-950">Transaction activity</h2>
          <p className="mt-1 text-xs text-slate-500">Total and flagged payments over time</p>
        </div>
        <div aria-label="Chart time range" className="flex rounded-lg bg-slate-100 p-1" role="group">
          {['24h', '30d'].map((option) => (
            <button
              aria-pressed={period === option}
              className={
                period === option
                  ? 'rounded-md bg-white px-3 py-1.5 text-xs font-semibold text-slate-900 shadow-sm'
                  : 'rounded-md px-3 py-1.5 text-xs font-medium text-slate-500 hover:text-slate-900'
              }
              key={option}
              onClick={() => onPeriodChange(option)}
              type="button"
            >
              {option === '24h' ? '24 hours' : '30 days'}
            </button>
          ))}
        </div>
      </div>

      {data.length ? (
        <div aria-label="Line chart of total and flagged transactions" className="mt-5 h-64 w-full">
          <ResponsiveContainer height="100%" width="100%">
            <LineChart data={data} margin={{ top: 8, right: 8, bottom: 0, left: -18 }}>
              <CartesianGrid stroke="#e2e8f0" strokeDasharray="3 3" vertical={false} />
              <XAxis
                axisLine={false}
                dataKey="t"
                tickFormatter={(value) => formatTick(value, period)}
                tickLine={false}
                tick={{ fill: '#64748b', fontSize: 11 }}
                minTickGap={24}
              />
              <YAxis
                allowDecimals={false}
                axisLine={false}
                tickLine={false}
                tick={{ fill: '#64748b', fontSize: 11 }}
                width={42}
              />
              <Tooltip
                labelFormatter={formatLabel}
                contentStyle={{ borderRadius: 12, borderColor: '#e2e8f0', fontSize: 12 }}
              />
              <Legend />
              <Line
                activeDot={{ r: 5 }}
                dataKey="total"
                dot={false}
                name="Total"
                stroke="#0f766e"
                strokeWidth={2.5}
                type="monotone"
              />
              <Line
                activeDot={{ r: 5 }}
                dataKey="flagged"
                dot={false}
                name="Flagged"
                stroke="#f59e0b"
                strokeWidth={2.5}
                type="monotone"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <div className="mt-5 grid h-64 place-items-center rounded-xl bg-slate-50 text-sm text-slate-500">
          No transaction activity for this range.
        </div>
      )}
    </section>
  )
}
