const cardKeys = ['total', 'flagged', 'rate', 'average']
const rowKeys = ['one', 'two', 'three', 'four', 'five']

export default function DashboardSkeleton() {
  return (
    <div aria-busy="true" aria-label="Loading dashboard" className="space-y-8">
      <div className="space-y-3">
        <div className="h-3 w-20 animate-pulse rounded bg-slate-200" />
        <div className="h-9 w-64 animate-pulse rounded bg-slate-200" />
        <div className="h-4 w-96 max-w-full animate-pulse rounded bg-slate-200" />
      </div>

      <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {cardKeys.map((key) => (
          <div className="h-32 animate-pulse rounded-2xl border border-slate-200 bg-white p-5" key={key}>
            <div className="h-4 w-28 rounded bg-slate-200" />
            <div className="mt-5 h-8 w-24 rounded bg-slate-200" />
            <div className="mt-3 h-3 w-36 rounded bg-slate-100" />
          </div>
        ))}
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        {['trend', 'histogram'].map((key) => (
          <div className="h-80 animate-pulse rounded-2xl border border-slate-200 bg-white p-5" key={key}>
            <div className="h-5 w-40 rounded bg-slate-200" />
            <div className="mt-6 h-56 rounded-xl bg-slate-100" />
          </div>
        ))}
      </section>

      <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white p-5">
        <div className="h-5 w-48 rounded bg-slate-200" />
        {rowKeys.map((key) => (
          <div className="mt-5 h-9 animate-pulse rounded bg-slate-100" key={key} />
        ))}
      </section>
      <span className="sr-only" role="status">Loading dashboard data</span>
    </div>
  )
}
