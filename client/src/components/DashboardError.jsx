export default function DashboardError({ message, onRetry }) {
  return (
    <section
      aria-labelledby="dashboard-error-title"
      className="rounded-2xl border border-rose-200 bg-white px-6 py-12 text-center shadow-sm"
      role="alert"
    >
      <div className="mx-auto grid h-12 w-12 place-items-center rounded-full bg-rose-50 text-lg font-bold text-rose-700">
        !
      </div>
      <h1 className="mt-4 text-xl font-bold text-slate-950" id="dashboard-error-title">
        Dashboard data could not load
      </h1>
      <p className="mx-auto mt-2 max-w-lg text-sm leading-6 text-slate-600">{message}</p>
      <button
        className="mt-6 rounded-xl bg-emerald-700 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-emerald-800"
        onClick={onRetry}
        type="button"
      >
        Retry
      </button>
    </section>
  )
}
