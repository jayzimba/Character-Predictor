import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  fetchDemoDataset,
  previewCollectedAssessments,
  validateDemoDataset,
  validateUploadedDataset,
} from '../../api/datasets'

function CountTable({ title, counts }) {
  const entries = Object.entries(counts || {})
  if (!entries.length) {
    return null
  }
  return (
    <div className="rounded-xl border border-line bg-card p-4">
      <h3 className="text-sm font-medium text-ink">{title}</h3>
      <dl className="mt-3 grid gap-2 text-sm sm:grid-cols-2">
        {entries.map(([key, value]) => (
          <div key={key} className="flex justify-between gap-4">
            <dt className="text-slate">{key}</dt>
            <dd className="font-medium text-ink">{value}</dd>
          </div>
        ))}
      </dl>
    </div>
  )
}

export default function DatasetPage() {
  const [demo, setDemo] = useState(null)
  const [report, setReport] = useState(null)
  const [error, setError] = useState(null)
  const [busy, setBusy] = useState(null)

  useEffect(() => {
    fetchDemoDataset()
      .then((response) => setDemo(response.data.data))
      .catch((err) => {
        setError(err.response?.data?.message || 'Could not load DEMO dataset metadata.')
      })
  }, [])

  async function run(label, action) {
    setBusy(label)
    setError(null)
    try {
      const response = await action()
      setReport(response.data.data)
    } catch (err) {
      setError(err.response?.data?.message || 'Validation failed.')
    } finally {
      setBusy(null)
    }
  }

  return (
    <div>
      <p className="text-sm font-medium text-teal">Phase 10</p>
      <h1 className="mt-1 font-serif text-3xl text-ink">Dataset preprocessing</h1>
      <p className="mt-2 max-w-2xl text-slate">
        Validate a CSV, drop unusable rows, and roll Likert answers into
        category scores. This step prepares features. It does not train a
        model or invent accuracy numbers. When a split is ready, fit the
        classifiers on the{' '}
        <Link to="/admin/training" className="text-teal hover:text-teal-dark">
          Training
        </Link>{' '}
        page.
      </p>

      {demo && (
        <p className="mt-6 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-950">
          Bundled file <span className="font-medium">{demo.filename}</span> is{' '}
          {demo.disclaimer}
        </p>
      )}

      <div className="mt-6 flex flex-wrap items-center gap-3">
        <button
          type="button"
          disabled={Boolean(busy)}
          onClick={() => run('demo', validateDemoDataset)}
          className="rounded-md bg-teal px-4 py-2 text-sm font-medium text-white hover:bg-teal-dark disabled:opacity-60"
        >
          {busy === 'demo' ? 'Validating…' : 'Validate DEMO CSV'}
        </button>
        <button
          type="button"
          disabled={Boolean(busy)}
          onClick={() => run('collected', previewCollectedAssessments)}
          className="rounded-md border border-line bg-card px-4 py-2 text-sm font-medium text-ink hover:bg-paper disabled:opacity-60"
        >
          {busy === 'collected' ? 'Reading…' : 'Preview completed assessments'}
        </button>
        <label className="rounded-md border border-line bg-card px-4 py-2 text-sm font-medium text-ink hover:bg-paper">
          {busy === 'upload' ? 'Uploading…' : 'Upload CSV'}
          <input
            type="file"
            accept=".csv,text/csv"
            className="sr-only"
            disabled={Boolean(busy)}
            onChange={(event) => {
              const file = event.target.files?.[0]
              event.target.value = ''
              if (file) {
                run('upload', () => validateUploadedDataset(file))
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

      {report && (
        <section className="mt-8 space-y-6">
          <div className="rounded-xl border border-line bg-card p-5">
            <h2 className="font-serif text-2xl text-ink">Validation report</h2>
            <p className="mt-2 text-sm text-slate">{report.disclaimer}</p>
            <p className="mt-3 text-sm text-ink">
              Source <span className="font-medium">{report.source}</span>
              {report.is_synthetic ? ' · DEMO/SYNTHETIC' : ''}
              {report.trained ? ' · trained' : ' · not trained'}
            </p>
            <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-2 lg:grid-cols-4">
              <div>
                <dt className="text-muted">Rows in</dt>
                <dd className="text-lg text-ink">{report.rows_in}</dd>
              </div>
              <div>
                <dt className="text-muted">Rows kept</dt>
                <dd className="text-lg text-ink">{report.rows_kept}</dd>
              </div>
              <div>
                <dt className="text-muted">Duplicates removed</dt>
                <dd className="text-lg text-ink">{report.duplicates_removed}</dd>
              </div>
              <div>
                <dt className="text-muted">Ready for later training</dt>
                <dd className="text-lg text-ink">{report.ready_for_training ? 'Yes' : 'No'}</dd>
              </div>
            </dl>
            <p className="mt-4 text-sm text-slate">{report.scaling_note}</p>
          </div>

          {(report.warnings?.length || report.errors?.length) && (
            <ul className="space-y-2 text-sm">
              {report.errors?.map((item) => (
                <li key={item} className="text-red-800">
                  {item}
                </li>
              ))}
              {report.warnings?.map((item) => (
                <li key={item} className="text-amber-950">
                  {item}
                </li>
              ))}
            </ul>
          )}

          <div className="grid gap-4 lg:grid-cols-2">
            <CountTable title="Class counts (kept rows)" counts={report.class_counts} />
            <CountTable title="Row origin" counts={report.origin_counts} />
          </div>

          {report.split && (
            <div className="rounded-xl border border-line bg-card p-4 text-sm">
              <h3 className="font-medium text-ink">Stratified split (not used for training yet)</h3>
              <p className="mt-2 text-slate">
                {report.split.train_size} train · {report.split.held_out_size} held-out · random_state{' '}
                {report.split.random_state}
              </p>
            </div>
          )}

          {report.preview?.length > 0 && (
            <div className="overflow-x-auto rounded-xl border border-line bg-card">
              <table className="min-w-full text-left text-xs">
                <thead className="border-b border-line text-muted">
                  <tr>
                    {Object.keys(report.preview[0]).map((column) => (
                      <th key={column} className="whitespace-nowrap px-3 py-2 font-medium">
                        {column}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {report.preview.map((row, index) => (
                    <tr key={index} className="border-b border-line last:border-b-0">
                      {Object.values(row).map((value, cell) => (
                        <td key={cell} className="whitespace-nowrap px-3 py-2 text-ink">
                          {String(value)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      )}
    </div>
  )
}
