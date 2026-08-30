import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  activateModel,
  activateSelectedModel,
  evaluateDemoModels,
  fetchLastEvaluation,
  fetchModelRegistry,
} from '../../api/evaluation'

function formatPercent(value) {
  if (typeof value !== 'number' || Number.isNaN(value)) {
    return '—'
  }
  return `${(value * 100).toFixed(1)}%`
}

function ComparisonTable({ scores }) {
  if (!scores?.length) {
    return null
  }
  return (
    <div className="overflow-x-auto rounded-xl border border-line bg-card">
      <table className="min-w-full text-left text-sm">
        <thead className="border-b border-line text-xs uppercase tracking-wide text-muted">
          <tr>
            <th className="px-4 py-3">Algorithm</th>
            <th className="px-4 py-3">Accuracy</th>
            <th className="px-4 py-3">Precision (macro)</th>
            <th className="px-4 py-3">Recall (macro)</th>
            <th className="px-4 py-3">F1 (macro)</th>
            <th className="px-4 py-3">F1 (weighted)</th>
            <th className="px-4 py-3">Selected</th>
          </tr>
        </thead>
        <tbody>
          {scores.map((row) => (
            <tr key={row.algorithm} className="border-b border-line last:border-b-0">
              <td className="px-4 py-3 text-ink">{row.algorithm}</td>
              <td className="px-4 py-3 text-slate">{formatPercent(row.accuracy)}</td>
              <td className="px-4 py-3 text-slate">{formatPercent(row.precision_macro)}</td>
              <td className="px-4 py-3 text-slate">{formatPercent(row.recall_macro)}</td>
              <td className="px-4 py-3 text-slate">{formatPercent(row.f1_macro)}</td>
              <td className="px-4 py-3 text-slate">{formatPercent(row.f1_weighted)}</td>
              <td className="px-4 py-3 text-slate">{row.selected ? 'Yes' : 'No'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function Confusion({ matrix }) {
  if (!matrix?.labels || !matrix?.matrix) {
    return null
  }
  return (
    <div className="overflow-x-auto rounded-xl border border-line bg-card p-4">
      <h3 className="text-sm font-medium text-ink">Confusion matrix (selected model)</h3>
      <table className="mt-3 min-w-full text-left text-xs">
        <thead>
          <tr>
            <th className="px-2 py-1 text-muted">Actual \ Pred</th>
            {matrix.labels.map((label) => (
              <th key={label} className="px-2 py-1 text-muted">
                {label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {matrix.matrix.map((row, index) => (
            <tr key={matrix.labels[index]}>
              <th className="px-2 py-1 text-muted">{matrix.labels[index]}</th>
              {row.map((cell, cellIndex) => (
                <td key={cellIndex} className="px-2 py-1 text-ink">
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default function ModelsPage() {
  const [evaluation, setEvaluation] = useState(null)
  const [registry, setRegistry] = useState([])
  const [error, setError] = useState(null)
  const [busy, setBusy] = useState(false)

  function load() {
    return Promise.all([fetchLastEvaluation(), fetchModelRegistry()]).then(
      ([evalResponse, registryResponse]) => {
        setEvaluation(evalResponse.data.data)
        setRegistry(registryResponse.data.data ?? [])
      }
    )
  }

  useEffect(() => {
    load().catch((err) => {
      setError(err.response?.data?.message || 'Could not load the model registry.')
    })
  }, [])

  async function evaluateDemo() {
    setBusy(true)
    setError(null)
    try {
      const response = await evaluateDemoModels()
      setEvaluation(response.data.data)
      const registryResponse = await fetchModelRegistry()
      setRegistry(registryResponse.data.data ?? [])
    } catch (err) {
      setError(err.response?.data?.message || 'Evaluation failed. Train the models first.')
    } finally {
      setBusy(false)
    }
  }

  const selected = evaluation?.scores?.find((row) => row.selected)

  return (
    <div>
      <p className="text-sm font-medium text-teal">Phase 12</p>
      <h1 className="mt-1 font-serif text-3xl text-ink">Model registry</h1>
      <p className="mt-2 max-w-2xl text-slate">
        Compare Decision Tree, Naive Bayes and KNN on the held-out fold. Every
        percentage is computed by scikit-learn. The selected model is recorded
        here; it is not served to users until the prediction phase.
      </p>
      <p className="mt-3 text-sm text-slate">
        Fit the estimators on the{' '}
        <Link to="/admin/training" className="text-teal hover:text-teal-dark">
          Training
        </Link>{' '}
        page first.
      </p>

      <p className="mt-6 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-950">
        DEMO/SYNTHETIC test scores can look perfect because the seed labels are
        constructed. Do not put them in the project report as research findings.
      </p>

      <button
        type="button"
        disabled={busy}
        onClick={evaluateDemo}
        className="mt-6 rounded-md bg-teal px-4 py-2 text-sm font-medium text-white hover:bg-teal-dark disabled:opacity-60"
      >
        {busy ? 'Evaluating…' : 'Evaluate DEMO held-out set'}
      </button>
      <button
        type="button"
        disabled={busy || !evaluation?.selected_model_id}
        onClick={async () => {
          setBusy(true)
          setError(null)
          try {
            await activateSelectedModel()
            const registryResponse = await fetchModelRegistry()
            setRegistry(registryResponse.data.data ?? [])
          } catch (err) {
            setError(err.response?.data?.message || 'Could not activate the selected model.')
          } finally {
            setBusy(false)
          }
        }}
        className="mt-6 ml-3 rounded-md border border-line bg-card px-4 py-2 text-sm font-medium text-ink hover:bg-paper disabled:opacity-60"
      >
        Activate selected model
      </button>

      {error && (
        <p className="mt-6 text-sm text-red-800" role="alert">
          {error}
        </p>
      )}

      {evaluation && (
        <section className="mt-8 space-y-6">
          <div className="rounded-xl border border-line bg-card p-5">
            <h2 className="font-serif text-2xl text-ink">Last comparison</h2>
            <p className="mt-2 text-sm text-slate">{evaluation.disclaimer}</p>
            <p className="mt-3 text-sm text-ink">
              {evaluation.dataset_name}
              {evaluation.is_synthetic ? ' · DEMO/SYNTHETIC' : ''}
              {' · '}
              {evaluation.n_test} held-out rows
              {evaluation.version ? ` · ${evaluation.version}` : ''}
            </p>
            <p className="mt-2 text-sm text-slate">{evaluation.selection_rule}</p>
            <p className="mt-2 text-sm text-ink">
              Selected: <span className="font-medium">{evaluation.selected_algorithm}</span>
            </p>
          </div>

          {evaluation.warnings?.map((item) => (
            <p key={item} className="text-sm text-amber-950">
              {item}
            </p>
          ))}

          <ComparisonTable scores={evaluation.scores} />
          <Confusion matrix={selected?.confusion_matrix} />
        </section>
      )}

      <section className="mt-10">
        <h2 className="font-serif text-2xl text-ink">Stored models</h2>
        <p className="mt-2 text-sm text-slate">
          Rows are written to <code>ml_models</code> and <code>model_metrics</code>.
          Activate one model so the prediction API can load it. Only one row is
          ACTIVE at a time.
        </p>
        <div className="mt-4 overflow-x-auto rounded-xl border border-line bg-card">
          <table className="min-w-full text-left text-sm">
            <thead className="border-b border-line text-xs uppercase tracking-wide text-muted">
              <tr>
                <th className="px-4 py-3">ID</th>
                <th className="px-4 py-3">Algorithm</th>
                <th className="px-4 py-3">Version</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">F1 macro</th>
                <th className="px-4 py-3">Synthetic</th>
                <th className="px-4 py-3">Action</th>
              </tr>
            </thead>
            <tbody>
              {registry.length === 0 && (
                <tr>
                  <td className="px-4 py-3 text-slate" colSpan={7}>
                    No evaluated models in the registry yet.
                  </td>
                </tr>
              )}
              {registry.map((row) => (
                <tr key={row.id} className="border-b border-line last:border-b-0">
                  <td className="px-4 py-3 text-muted">{row.id}</td>
                  <td className="px-4 py-3 text-ink">{row.algorithm}</td>
                  <td className="px-4 py-3 text-slate">{row.version}</td>
                  <td className="px-4 py-3 text-slate">{row.status}</td>
                  <td className="px-4 py-3 text-slate">
                    {row.metrics ? formatPercent(row.metrics.f1_macro) : '—'}
                  </td>
                  <td className="px-4 py-3 text-slate">
                    {row.is_synthetic_dataset ? 'DEMO' : 'Collected'}
                  </td>
                  <td className="px-4 py-3">
                    {row.status === 'ACTIVE' ? (
                      <span className="text-xs uppercase tracking-wide text-teal">Active</span>
                    ) : (
                      <button
                        type="button"
                        disabled={busy}
                        onClick={async () => {
                          setBusy(true)
                          setError(null)
                          try {
                            await activateModel(row.id)
                            const registryResponse = await fetchModelRegistry()
                            setRegistry(registryResponse.data.data ?? [])
                          } catch (err) {
                            setError(err.response?.data?.message || 'Could not activate this model.')
                          } finally {
                            setBusy(false)
                          }
                        }}
                        className="text-sm text-teal hover:text-teal-dark"
                      >
                        Activate
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  )
}
