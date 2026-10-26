const riskOptions = ['LOW', 'MEDIUM', 'HIGH', 'UNSCORED']

export default function FlaggedFilterBar({ filters, onChange, onApply, onClear }) {
  return (
    <form
      className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm"
      onSubmit={onApply}
    >
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-[1.2fr_1fr_1fr_auto_auto] xl:items-end">
        <div>
          <label className="text-xs font-semibold uppercase tracking-wide text-slate-500" htmlFor="riskLabel">
            Risk label
          </label>
          <select
            className="mt-2 w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm text-slate-800 outline-none focus:border-emerald-600 focus:ring-4 focus:ring-emerald-100"
            id="riskLabel"
            onChange={(event) => onChange('riskLabel', event.target.value)}
            value={filters.riskLabel}
          >
            <option value="">All risk labels</option>
            {riskOptions.map((riskLabel) => (
              <option key={riskLabel} value={riskLabel}>{riskLabel}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="text-xs font-semibold uppercase tracking-wide text-slate-500" htmlFor="from">
            From
          </label>
          <input
            className="mt-2 w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm text-slate-800 outline-none focus:border-emerald-600 focus:ring-4 focus:ring-emerald-100"
            id="from"
            max={filters.to || undefined}
            onChange={(event) => onChange('from', event.target.value)}
            type="date"
            value={filters.from}
          />
        </div>

        <div>
          <label className="text-xs font-semibold uppercase tracking-wide text-slate-500" htmlFor="to">
            To
          </label>
          <input
            className="mt-2 w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm text-slate-800 outline-none focus:border-emerald-600 focus:ring-4 focus:ring-emerald-100"
            id="to"
            min={filters.from || undefined}
            onChange={(event) => onChange('to', event.target.value)}
            type="date"
            value={filters.to}
          />
        </div>

        <button
          className="rounded-xl bg-emerald-700 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-emerald-800"
          type="submit"
        >
          Apply filters
        </button>
        <button
          className="rounded-xl border border-slate-200 px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
          onClick={onClear}
          type="button"
        >
          Clear
        </button>
      </div>
    </form>
  )
}
