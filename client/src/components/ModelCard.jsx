import { useCallback, useEffect, useState } from 'react'
import apiClient, { getApiErrorMessage } from '../api/client'

const metricLabels = [
  ['Precision', 'precision'],
  ['Recall', 'recall'],
  ['F1 score', 'f1'],
  ['ROC-AUC', 'roc_auc'],
  ['PR-AUC', 'pr_auc'],
]

function formatPercent(value) {
  const number = Number(value)
  return Number.isFinite(number)
    ? new Intl.NumberFormat(undefined, { style: 'percent', maximumFractionDigits: 1 }).format(number)
    : '—'
}

function MatrixGrid({ matrix }) {
  const validMatrix =
    Array.isArray(matrix) &&
    matrix.length === 2 &&
    matrix.every((row) => Array.isArray(row) && row.length === 2)

  if (!validMatrix) {
    return <p className="text-sm text-slate-500">Confusion matrix unavailable.</p>
  }

  return (
    <div aria-label="Confusion matrix" className="grid w-40 grid-cols-2 gap-2" role="group">
      {matrix.map((row, rowIndex) =>
        row.map((value, columnIndex) => (
          <div
            aria-label={'Row ' + (rowIndex + 1) + ', column ' + (columnIndex + 1) + ': ' + value}
            className="grid aspect-square place-items-center rounded-xl border border-emerald-100 bg-emerald-50 text-lg font-bold text-emerald-900"
            key={rowIndex + '-' + columnIndex}
          >
            {new Intl.NumberFormat().format(value)}
          </div>
        )),
      )}
    </div>
  )
}

export default function ModelCard() {
  const [model, setModel] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const loadModel = useCallback(async () => {
    setLoading(true)
    setError('')

    try {
      const { data } = await apiClient.get('/api/model-info')
      setModel(data)
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, 'Could not load model information.'))
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void loadModel()
  }, [loadModel])

  if (loading) {
    return (
      <section aria-busy="true" className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="h-5 w-36 animate-pulse rounded bg-slate-200" />
        <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-5">
          {metricLabels.map(([label]) => (
            <div className="h-16 animate-pulse rounded-xl bg-slate-100" key={label} />
          ))}
        </div>
        <span className="sr-only" role="status">Loading model information</span>
      </section>
    )
  }

  if (error) {
    return (
      <section className="rounded-2xl border border-rose-200 bg-white p-5 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-base font-bold text-slate-950">Model</h2>
            <p className="mt-1 text-sm text-rose-700">{error}</p>
          </div>
          <button
            className="rounded-lg border border-slate-200 px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
            onClick={loadModel}
            type="button"
          >
            Retry
          </button>
        </div>
      </section>
    )
  }

  const metrics = model.metrics || {}

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="text-base font-bold text-slate-950">Model</h2>
          <p className="mt-1 text-xs text-slate-500">Model performance and decision threshold</p>
        </div>
        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">
          {model.model_version}
        </span>
      </div>

      <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-3 xl:grid-cols-6">
        <div className="rounded-xl bg-emerald-50 p-3">
          <p className="text-xs font-medium text-emerald-800">Threshold</p>
          <p className="mt-1 text-lg font-bold text-emerald-950">{formatPercent(model.threshold)}</p>
        </div>
        {metricLabels.map(([label, key]) => (
          <div className="rounded-xl bg-slate-50 p-3" key={key}>
            <p className="text-xs font-medium text-slate-500">{label}</p>
            <p className="mt-1 text-lg font-bold text-slate-900">{formatPercent(metrics[key])}</p>
          </div>
        ))}
      </div>

      <div className="mt-5 border-t border-slate-100 pt-5">
        <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
          Confusion matrix
        </p>
        <MatrixGrid matrix={metrics.confusion_matrix} />
      </div>
    </section>
  )
}
