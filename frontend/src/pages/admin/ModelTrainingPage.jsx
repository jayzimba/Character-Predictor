import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { fetchLastTrainingRun, trainDemoModels, trainUploadedModels } from '../../api/training'
import TableShell from '../../components/ui/TableShell'

function formatPercent(value) {
  if (typeof value !== 'number' || Number.isNaN(value)) {
    return '—'
  }
  return `${(value * 100).toFixed(1)}%`
}

export default function ModelTrainingPage() {
  const [run, setRun] = useState(null)
  const [error, setError] = useState(null)
  const [busy, setBusy] = useState(null)

  useEffect(() => {
    fetchLastTrainingRun()
      .then((response) => setRun(response.data.data))
      .catch((err) => {
        setError(err.response?.data?.message || 'Could not load the last training run.')
      })
  }, [])

  async function runTraining(label, action) {
    setBusy(label)
    setError(null)
    try {
      const response = await action()
      setRun(response.data.data)
    } catch (err) {
      setError(err.response?.data?.message || 'Training failed.')
    } finally {
      setBusy(null)
    }
  }

  return (
    <div>
      <p className="text-sm font-medium text-teal">Phase 11</p>
      <h1 className="mt-1 font-serif text-3xl text-ink">Model training</h1>
      <p className="mt-2 max-w-2xl text-slate">
        Fit Decision Tree, Naive Bayes and KNN on the same stratified training
        fold. KNN scales inside a scikit-learn Pipeline. After fitting, evaluate
        the held-out fold on the{' '}
        <Link to="/admin/models" className="text-teal hover:text-teal-dark">
          Models
        </Link>{' '}
        page.
      </p>
      <p className="mt-3 text-sm text-slate">
        Prepare or inspect the CSV on the{' '}
        <Link to="/admin/dataset" className="text-teal hover:text-teal-dark">
          Dataset
        </Link>{' '}
        page first.
      </p>

      <p className="mt-6 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-950">
        Training the bundled file produces DEMO/SYNTHETIC models. Do not report
        those fits, or their training-fold scores, as research findings.
      </p>

      <div className="mt-6 flex flex-wrap items-center gap-3">
        <button
          type="button"
          disabled={Boolean(busy)}
          onClick={() => runTraining('demo', trainDemoModels)}
          className="rounded-md bg-teal px-4 py-2 text-sm font-medium text-white hover:bg-teal-dark disabled:opacity-60"
        >
          {busy === 'demo' ? 'Fitting…' : 'Train DEMO models'}
        </button>
        <label className="rounded-md border border-line bg-card px-4 py-2 text-sm font-medium text-ink hover:bg-paper">
          {busy === 'upload' ? 'Fitting…' : 'Train uploaded CSV'}
          <input
            type="file"
            accept=".csv,text/csv"
            className="sr-only"
            disabled={Boolean(busy)}
            onChange={(event) => {
              const file = event.target.files?.[0]
              event.target.value = ''
              if (file) {
                runTraining('upload', () => trainUploadedModels(file))
              }
            }}
          />
        </label>
      </div>

      {error && (
        <p className="mt-6 text-sm text-red-800" role="alert">
          {error}
        </p>
      )}

      {run && (
        <section className="mt-8 space-y-6">
          <div className="rounded-xl border border-line bg-card p-5">
            <h2 className="font-serif text-2xl text-ink">Last training run</h2>
            <p className="mt-2 text-sm text-slate">{run.disclaimer}</p>
            <p className="mt-3 text-sm text-ink">
              Source <span className="font-medium">{run.dataset_name}</span>
              {run.is_synthetic ? ' · DEMO/SYNTHETIC' : ''}
              {run.held_out_evaluated ? ' · test evaluated' : ' · held-out not evaluated'}
              {run.registered ? ' · registered' : ' · not in registry'}
            </p>
            <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-2 lg:grid-cols-4">
              <div>
                <dt className="text-muted">Training rows</dt>
                <dd className="text-lg text-ink">{run.n_train}</dd>
              </div>
              <div>
                <dt className="text-muted">Held-out rows (unused)</dt>
                <dd className="text-lg text-ink">{run.n_test}</dd>
              </div>
              <div>
                <dt className="text-muted">Features</dt>
                <dd className="text-lg text-ink">{run.feature_names?.length ?? 0}</dd>
              </div>
              <div>
                <dt className="text-muted">random_state</dt>
                <dd className="text-lg text-ink">{run.random_state}</dd>
              </div>
            </dl>
            <p className="mt-4 text-sm text-slate">{run.cv_note}</p>
          </div>

          {run.warnings?.length > 0 && (
            <ul className="space-y-2 text-sm text-amber-950">
              {run.warnings.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          )}

          <TableShell className="">
            <table className="min-w-full text-left text-sm">
              <thead className="border-b border-line text-xs uppercase tracking-wide text-muted">
                <tr>
                  <th className="px-4 py-3">Algorithm</th>
                  <th className="px-4 py-3">Estimator</th>
                  <th className="px-4 py-3">Scaler</th>
                  <th className="px-4 py-3">Train-fold CV</th>
                  <th className="px-4 py-3">File</th>
                </tr>
              </thead>
              <tbody>
                {run.models.map((model) => (
                  <tr key={model.algorithm} className="border-b border-line last:border-b-0">
                    <td className="px-4 py-3 text-ink">{model.algorithm}</td>
                    <td className="px-4 py-3 text-slate">{model.sklearn_class}</td>
                    <td className="px-4 py-3 text-slate">
                      {model.uses_scaler ? 'In pipeline' : 'Not used'}
                    </td>
                    <td className="px-4 py-3 text-slate">
                      {model.cv
                        ? `${formatPercent(model.cv.mean)} ± ${formatPercent(model.cv.std)}`
                        : 'Skipped'}
                    </td>
                    <td className="px-4 py-3 text-slate">{model.file_name}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </TableShell>
        </section>
      )}
    </div>
  )
}
