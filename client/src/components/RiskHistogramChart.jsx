import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

export default function RiskHistogramChart({ bins }) {
  const chartData = bins.map((bin) => ({
    label: Math.round(bin.from * 100) + '-' + Math.round(bin.to * 100) + '%',
    count: bin.count,
  }))

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div>
        <h2 className="text-base font-bold text-slate-950">Risk score distribution</h2>
        <p className="mt-1 text-xs text-slate-500">Transaction counts by probability range</p>
      </div>

      {chartData.length ? (
        <div aria-label="Bar chart of risk score histogram" className="mt-5 h-64 w-full">
          <ResponsiveContainer height="100%" width="100%">
            <BarChart data={chartData} margin={{ top: 8, right: 8, bottom: 0, left: -18 }}>
              <CartesianGrid stroke="#e2e8f0" strokeDasharray="3 3" vertical={false} />
              <XAxis
                axisLine={false}
                dataKey="label"
                tickLine={false}
                tick={{ fill: '#64748b', fontSize: 10 }}
                interval={0}
              />
              <YAxis
                allowDecimals={false}
                axisLine={false}
                tickLine={false}
                tick={{ fill: '#64748b', fontSize: 11 }}
                width={42}
              />
              <Tooltip contentStyle={{ borderRadius: 12, borderColor: '#e2e8f0', fontSize: 12 }} />
              <Bar dataKey="count" fill="#0f766e" radius={[5, 5, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <div className="mt-5 grid h-64 place-items-center rounded-xl bg-slate-50 text-sm text-slate-500">
          No scored transactions yet.
        </div>
      )}
    </section>
  )
}
