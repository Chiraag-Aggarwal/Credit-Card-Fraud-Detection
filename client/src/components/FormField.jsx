export default function FormField({
  id,
  label,
  type = 'text',
  value,
  onChange,
  autoComplete,
  placeholder,
  required = true,
  minLength,
  error,
}) {
  const inputClass = error
    ? 'mt-2 w-full rounded-xl border border-rose-300 bg-white px-4 py-3 text-sm text-slate-900 outline-none ring-2 ring-rose-100'
    : 'mt-2 w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-emerald-600 focus:ring-4 focus:ring-emerald-100'

  return (
    <div>
      <label className="text-sm font-semibold text-slate-700" htmlFor={id}>
        {label}
      </label>
      <input
        aria-describedby={error ? id + '-error' : undefined}
        aria-invalid={Boolean(error)}
        autoComplete={autoComplete}
        className={inputClass}
        id={id}
        minLength={minLength}
        name={id}
        onChange={onChange}
        placeholder={placeholder}
        required={required}
        type={type}
        value={value}
      />
      {error && (
        <p className="mt-1.5 text-xs font-medium text-rose-700" id={id + '-error'}>
          {error}
        </p>
      )}
    </div>
  )
}
