import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  activateModel,
  activateSelectedModel,
  archiveModel,
  evaluateDemoModels,
  fetchLastEvaluation,
  fetchModelRegistry,
  updateModelNotes,
} from '../../api/evaluation'
import Field, { selectClass } from '../../components/public/Field'
import TableShell from '../../components/ui/TableShell'
import IconButton, {
  ArchiveIcon,
  ChevronIcon,
  EyeIcon,
  PencilIcon,
  PlayIcon,
} from '../../components/ui/IconButton'
import Modal from '../../components/ui/Modal'

const PAGE_SIZE = 10

function formatPercent(value) {
  if (typeof value !== 'number' || Number.isNaN(value)) {
    return '—'
  }
  return `${(value * 100).toFixed(1)}%`
}

function formatDate(value) {
  if (!value) {
    return '—'
  }
  return new Intl.DateTimeFormat('en-GB', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  }).format(new Date(value))
}

function algorithmLabel(value) {
  return (value || '').replaceAll('_', ' ')
}

function ComparisonTable({ scores }) {
  if (!scores?.length) {
    return null
  }
  return (
    <TableShell className="">
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
              <td className="px-4 py-3 text-ink">{algorithmLabel(row.algorithm)}</td>
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
    </TableShell>
  )
}

function Confusion({ matrix }) {
  if (!matrix?.labels || !matrix?.matrix) {
    return null
  }
  return (
    <div className="overflow-x-auto rounded-xl border border-line bg-card p-4">
      <h3 className="text-sm font-medium text-ink">Confusion matrix</h3>
      <p className="mt-1 text-xs text-muted">Counts from the held-out fold for the selected algorithm.</p>
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

function Notice({ tone = 'slate', children }) {
  const tones = {
    slate: 'border-line bg-card text-slate',
    amber: 'border-amber-200 bg-amber-50 text-amber-950',
    teal: 'border-teal/30 bg-teal/5 text-teal-dark',
    danger: 'border-red-200 bg-red-50 text-red-800',
  }
  return (
    <p className={`rounded-xl border px-4 py-3 text-sm ${tones[tone]}`} role={tone === 'danger' ? 'alert' : undefined}>
      {children}
    </p>
  )
}

function buildNotices(evaluation, registry) {
  const active = registry.find((row) => row.status === 'ACTIVE')
  const items = []

  if (!evaluation) {
    items.push({
      tone: 'slate',
      text: 'No held-out comparison is stored yet. Train the classifiers, then evaluate this tab.',
    })
  } else if (evaluation.is_synthetic) {
    items.push({
      tone: 'amber',
      text: `${evaluation.dataset_name} is DEMO/SYNTHETIC (${evaluation.n_test} held-out rows). Scores can look perfect because the labels were constructed — do not put them in the report as research findings.`,
    })
  } else {
    items.push({
      tone: 'slate',
      text: `${evaluation.dataset_name}: ${evaluation.n_test} held-out rows. Percentages come from sklearn.metrics on that fold.`,
    })
  }

  if (!active) {
    items.push({
      tone: 'amber',
      text: 'No model is ACTIVE. New classifications will use DEMO MODE until you activate one from the Registry tab.',
    })
  } else {
    const label = `${algorithmLabel(active.algorithm)} (${active.version})`
    if (!active.artifact_present) {
      items.push({
        tone: 'danger',
        text: `${label} is marked ACTIVE but its joblib file is missing, so live prediction cannot load it.`,
      })
    } else if (active.is_synthetic_dataset) {
      items.push({
        tone: 'teal',
        text: `${label} is ACTIVE. It was fitted on DEMO/SYNTHETIC labels, so live results stay in DEMO MODE.`,
      })
    } else {
      items.push({
        tone: 'teal',
        text: `${label} is ACTIVE and serving live predictions. ${active.prediction_count ?? 0} stored prediction${active.prediction_count === 1 ? '' : 's'} point at this model.`,
      })
    }
  }

  return items
}

function TabButton({ id, label, count, current, onSelect }) {
  const selected = current === id
  return (
    <button
      type="button"
      role="tab"
      id={`models-tab-${id}`}
      aria-selected={selected}
      aria-controls={`models-panel-${id}`}
      onClick={() => onSelect(id)}
      className={`rounded-md px-4 py-2 text-sm font-medium ${
        selected ? 'bg-teal text-white' : 'text-slate hover:bg-sand hover:text-ink'
      }`}
    >
      {label}
      {typeof count === 'number' && (
        <span className={`ml-2 text-xs ${selected ? 'text-white/80' : 'text-muted'}`}>{count}</span>
      )}
    </button>
  )
}

export default function ModelsPage() {
  const [evaluation, setEvaluation] = useState(null)
  const [registry, setRegistry] = useState([])
  const [error, setError] = useState(null)
  const [message, setMessage] = useState(null)
  const [busy, setBusy] = useState(false)
  const [page, setPage] = useState(1)
  const [modal, setModal] = useState(null)
  const [notes, setNotes] = useState('')
  const [tab, setTab] = useState('comparison')
  const [loaded, setLoaded] = useState(false)

  function load() {
    return Promise.all([fetchLastEvaluation(), fetchModelRegistry()]).then(
      ([evalResponse, registryResponse]) => {
        setEvaluation(evalResponse.data.data)
        setRegistry(registryResponse.data.data ?? [])
      }
    )
  }

  useEffect(() => {
    load()
      .catch((err) => {
        setError(err.response?.data?.message || 'Could not load the model registry.')
      })
      .finally(() => setLoaded(true))
  }, [])

  const pageCount = Math.max(1, Math.ceil(registry.length / PAGE_SIZE))
  const currentPage = Math.min(page, pageCount)
  const visible = useMemo(() => {
    const start = (currentPage - 1) * PAGE_SIZE
    return registry.slice(start, start + PAGE_SIZE)
  }, [registry, currentPage])
  const rangeStart = registry.length === 0 ? 0 : (currentPage - 1) * PAGE_SIZE + 1
  const rangeEnd = Math.min(currentPage * PAGE_SIZE, registry.length)

  const selected = evaluation?.scores?.find((row) => row.selected)
  const activeModel = registry.find((row) => row.status === 'ACTIVE')
  const selectedIsActive = Boolean(
    evaluation?.selected_model_id &&
      registry.some((row) => row.id === evaluation.selected_model_id && row.status === 'ACTIVE')
  )
  const notices = useMemo(
    () => buildNotices(evaluation, registry),
    [evaluation, registry]
  )
  const viewRow = modal?.type === 'view' ? modal.row : null
  const activateRow = modal?.type === 'activate' ? modal.row : null
  const archiveRow = modal?.type === 'archive' ? modal.row : null
  const notesRow = modal?.type === 'notes' ? modal.row : null
  const activateSelectedOpen = modal?.type === 'activate-selected'

  function closeModal() {
    setModal(null)
    setError(null)
  }

  async function refreshRegistry() {
    const registryResponse = await fetchModelRegistry()
    setRegistry(registryResponse.data.data ?? [])
  }

  async function evaluateDemo() {
    setBusy(true)
    setError(null)
    setMessage(null)
    try {
      const response = await evaluateDemoModels()
      setEvaluation(response.data.data)
      await refreshRegistry()
      setTab('comparison')
      setMessage('Held-out metrics stored. Activate a model from Comparison or Registry to serve predictions.')
    } catch (err) {
      setError(err.response?.data?.message || 'Evaluation failed. Train the models first.')
    } finally {
      setBusy(false)
    }
  }

  async function confirmActivate(row) {
    setBusy(true)
    setError(null)
    try {
      await activateModel(row.id)
      await refreshRegistry()
      setTab('registry')
      setMessage(`${algorithmLabel(row.algorithm)} (${row.version}) is now ACTIVE.`)
      closeModal()
    } catch (err) {
      setError(err.response?.data?.message || 'Could not activate this model.')
    } finally {
      setBusy(false)
    }
  }

  async function confirmActivateSelected() {
    setBusy(true)
    setError(null)
    try {
      await activateSelectedModel()
      await refreshRegistry()
      setTab('registry')
      setMessage('The selected model is now ACTIVE. Previous active models were archived.')
      closeModal()
    } catch (err) {
      setError(err.response?.data?.message || 'Could not activate the selected model.')
    } finally {
      setBusy(false)
    }
  }

  async function confirmArchive(row) {
    setBusy(true)
    setError(null)
    try {
      await archiveModel(row.id)
      await refreshRegistry()
      setTab('registry')
      setMessage(`${algorithmLabel(row.algorithm)} (${row.version}) was archived.`)
      closeModal()
    } catch (err) {
      setError(err.response?.data?.message || 'Could not archive this model.')
    } finally {
      setBusy(false)
    }
  }

  async function saveNotes(event) {
    event.preventDefault()
    if (!notesRow) {
      return
    }
    setBusy(true)
    setError(null)
    try {
      await updateModelNotes(notesRow.id, notes)
      await refreshRegistry()
      setMessage('Notes saved. Metrics were not changed.')
      closeModal()
    } catch (err) {
      setError(err.response?.data?.message || 'Could not update notes.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div>
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-teal">Model administration</p>
          <h1 className="mt-1 font-serif text-3xl text-ink">Models</h1>
          <p className="mt-2 max-w-2xl text-slate">
            Compare held-out scores, then activate one registered artefact.
            Archive instead of deleting so past predictions keep their model.
            Train first on the{' '}
            <Link to="/admin/training" className="text-teal hover:text-teal-dark">
              Training
            </Link>{' '}
            page.
          </p>
        </div>
      </div>

      <div className="mt-6 space-y-3">
        {loaded &&
          notices.map((item) => (
            <Notice key={item.text} tone={item.tone}>
              {item.text}
            </Notice>
          ))}
        {error && !modal && <Notice tone="danger">{error}</Notice>}
        {message && <Notice tone="teal">{message}</Notice>}
      </div>

      <div
        role="tablist"
        aria-label="Model administration"
        className="mt-8 inline-flex flex-wrap gap-1 rounded-lg border border-line bg-card p-1"
      >
        <TabButton id="comparison" label="Comparison" current={tab} onSelect={setTab} />
        <TabButton
          id="registry"
          label="Registry"
          count={registry.length}
          current={tab}
          onSelect={setTab}
        />
      </div>

      {tab === 'comparison' && (
      <section
        id="models-panel-comparison"
        role="tabpanel"
        aria-labelledby="models-tab-comparison"
        className="mt-6 space-y-6"
      >
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="font-serif text-2xl text-ink">Last comparison</h2>
            <p className="mt-1 text-sm text-slate">
              Decision Tree, Naive Bayes and KNN on the same held-out fold.
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <button
              type="button"
              disabled={busy}
              onClick={evaluateDemo}
              className="rounded-md bg-teal px-4 py-2.5 text-sm font-medium text-white hover:bg-teal-dark disabled:opacity-60"
            >
              {busy ? 'Working…' : 'Evaluate DEMO held-out set'}
            </button>
            <button
              type="button"
              disabled={busy || !evaluation?.selected_model_id || selectedIsActive}
              onClick={() => setModal({ type: 'activate-selected' })}
              className="rounded-md border border-line bg-card px-4 py-2.5 text-sm font-medium text-ink hover:bg-paper disabled:opacity-60"
            >
              {selectedIsActive ? 'Selected model is ACTIVE' : 'Activate selected'}
            </button>
          </div>
        </div>

        {evaluation ? (
          <>
            <div className="rounded-xl border border-line bg-card p-5">
              <dl className="grid gap-3 text-sm sm:grid-cols-2 lg:grid-cols-4">
                <div>
                  <dt className="text-muted">Dataset</dt>
                  <dd className="mt-1 text-ink">
                    {evaluation.dataset_name}
                    {evaluation.is_synthetic ? ' · DEMO/SYNTHETIC' : ''}
                  </dd>
                </div>
                <div>
                  <dt className="text-muted">Held-out rows</dt>
                  <dd className="mt-1 text-ink">{evaluation.n_test}</dd>
                </div>
                <div>
                  <dt className="text-muted">Run</dt>
                  <dd className="mt-1 text-ink">{evaluation.version || '—'}</dd>
                </div>
                <div>
                  <dt className="text-muted">Winner</dt>
                  <dd className="mt-1 text-ink">{algorithmLabel(evaluation.selected_algorithm)}</dd>
                </div>
              </dl>
              <p className="mt-4 text-sm text-slate">{evaluation.selection_rule}</p>
            </div>

            <ComparisonTable scores={evaluation.scores} />
            <p className="text-xs text-muted">
              Percentages are stored sklearn.metrics values for this fold, not typed in by hand.
            </p>
            <Confusion matrix={selected?.confusion_matrix} />
          </>
        ) : (
          <p className="rounded-xl border border-line bg-card px-4 py-8 text-sm text-slate">
            Nothing to compare yet. Fit the estimators on Training, then evaluate the held-out set.
          </p>
        )}
      </section>
      )}

      {tab === 'registry' && (
      <section
        id="models-panel-registry"
        role="tabpanel"
        aria-labelledby="models-tab-registry"
        className="mt-6"
      >
        <h2 className="font-serif text-2xl text-ink">Stored models</h2>
        <p className="mt-2 text-sm text-slate">
          {activeModel
            ? `${algorithmLabel(activeModel.algorithm)} (${activeModel.version}) is serving predictions. Archive instead of deleting so history keeps its model_id.`
            : 'Activate one row so the prediction API can load it. Metrics stay as sklearn stored them.'}
        </p>
        <TableShell className="mt-4">
          <table className="min-w-full text-left text-sm">
            <thead className="border-b border-line text-xs uppercase tracking-wide text-muted">
              <tr>
                <th className="px-4 py-3">ID</th>
                <th className="px-4 py-3">Algorithm</th>
                <th className="px-4 py-3">Version</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">F1 macro</th>
                <th className="px-4 py-3">Predictions</th>
                <th className="px-4 py-3">Dataset</th>
                <th className="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {registry.length === 0 && (
                <tr>
                  <td className="px-4 py-3 text-slate" colSpan={8}>
                    No evaluated models in the registry yet.
                  </td>
                </tr>
              )}
              {visible.map((row) => (
                <tr key={row.id} className="border-b border-line last:border-b-0">
                  <td className="px-4 py-3 text-muted">{row.id}</td>
                  <td className="px-4 py-3 text-ink">{algorithmLabel(row.algorithm)}</td>
                  <td className="px-4 py-3 text-slate">{row.version}</td>
                  <td className="px-4 py-3 text-slate">{row.status}</td>
                  <td className="px-4 py-3 text-slate">
                    {row.metrics ? formatPercent(row.metrics.f1_macro) : '—'}
                  </td>
                  <td className="px-4 py-3 text-slate">{row.prediction_count ?? 0}</td>
                  <td className="px-4 py-3 text-slate">
                    {row.is_synthetic_dataset ? 'DEMO' : 'Collected'}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex justify-end gap-1">
                      <IconButton label="View model" tone="slate" onClick={() => setModal({ type: 'view', row })}>
                        <EyeIcon />
                      </IconButton>
                      <IconButton
                        label="Edit notes"
                        onClick={() => {
                          setNotes(row.notes || '')
                          setModal({ type: 'notes', row })
                        }}
                      >
                        <PencilIcon />
                      </IconButton>
                      {row.status !== 'ACTIVE' && (
                        <IconButton
                          label={row.artifact_present ? 'Activate model' : 'No artefact on disk'}
                          disabled={busy || !row.artifact_present}
                          onClick={() => setModal({ type: 'activate', row })}
                        >
                          <PlayIcon />
                        </IconButton>
                      )}
                      {row.status !== 'ARCHIVED' && (
                        <IconButton
                          label="Archive model"
                          tone="danger"
                          disabled={busy}
                          onClick={() => setModal({ type: 'archive', row })}
                        >
                          <ArchiveIcon />
                        </IconButton>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </TableShell>

        <div className="mt-4 flex flex-wrap items-center justify-between gap-3 text-sm text-slate">
          <p>
            Showing {rangeStart}–{rangeEnd} of {registry.length}
          </p>
          <div className="flex items-center gap-2">
            <IconButton
              label="Previous page"
              tone="slate"
              disabled={currentPage <= 1}
              onClick={() => setPage(currentPage - 1)}
            >
              <ChevronIcon direction="prev" />
            </IconButton>
            {Array.from({ length: pageCount }, (_, index) => {
              const number = index + 1
              const active = number === currentPage
              return (
                <button
                  key={number}
                  type="button"
                  onClick={() => setPage(number)}
                  className={`h-8 min-w-8 rounded-md px-2 ${
                    active ? 'bg-teal text-white' : 'text-slate hover:bg-sand'
                  }`}
                  aria-current={active ? 'page' : undefined}
                >
                  {number}
                </button>
              )
            })}
            <IconButton
              label="Next page"
              tone="slate"
              disabled={currentPage >= pageCount}
              onClick={() => setPage(currentPage + 1)}
            >
              <ChevronIcon direction="next" />
            </IconButton>
          </div>
        </div>
      </section>
      )}

      <Modal
        title="Model details"
        open={Boolean(viewRow)}
        onClose={closeModal}
        size="lg"
        footer={
          <button
            type="button"
            onClick={closeModal}
            className="rounded-md bg-teal px-4 py-2 text-sm font-medium text-white hover:bg-teal-dark"
          >
            Close
          </button>
        }
      >
        {viewRow && (
          <div className="space-y-5">
            <dl className="grid gap-3 text-sm sm:grid-cols-2">
              <div>
                <dt className="text-muted">Algorithm</dt>
                <dd className="mt-1 text-ink">{algorithmLabel(viewRow.algorithm)}</dd>
              </div>
              <div>
                <dt className="text-muted">Version</dt>
                <dd className="mt-1 text-ink">{viewRow.version}</dd>
              </div>
              <div>
                <dt className="text-muted">Status</dt>
                <dd className="mt-1 text-ink">{viewRow.status}</dd>
              </div>
              <div>
                <dt className="text-muted">Trained</dt>
                <dd className="mt-1 text-ink">{formatDate(viewRow.trained_at)}</dd>
              </div>
              <div>
                <dt className="text-muted">Dataset</dt>
                <dd className="mt-1 text-ink">
                  {viewRow.dataset_name}
                  {viewRow.is_synthetic_dataset ? ' · DEMO/SYNTHETIC' : ''}
                </dd>
              </div>
              <div>
                <dt className="text-muted">Split</dt>
                <dd className="mt-1 text-ink">
                  {viewRow.train_size} train · {viewRow.test_size} test
                </dd>
              </div>
              <div>
                <dt className="text-muted">Predictions stored</dt>
                <dd className="mt-1 text-ink">{viewRow.prediction_count ?? 0}</dd>
              </div>
              <div>
                <dt className="text-muted">Artefact</dt>
                <dd className="mt-1 text-ink">{viewRow.artifact_present ? 'On disk' : 'Missing'}</dd>
              </div>
            </dl>
            {viewRow.notes && (
              <div className="text-sm">
                <p className="text-muted">Notes</p>
                <p className="mt-1 text-ink">{viewRow.notes}</p>
              </div>
            )}
            {viewRow.metrics && (
              <dl className="grid gap-3 text-sm sm:grid-cols-3">
                <div>
                  <dt className="text-muted">Accuracy</dt>
                  <dd className="mt-1 text-ink">{formatPercent(viewRow.metrics.accuracy)}</dd>
                </div>
                <div>
                  <dt className="text-muted">F1 macro</dt>
                  <dd className="mt-1 text-ink">{formatPercent(viewRow.metrics.f1_macro)}</dd>
                </div>
                <div>
                  <dt className="text-muted">F1 weighted</dt>
                  <dd className="mt-1 text-ink">{formatPercent(viewRow.metrics.f1_weighted)}</dd>
                </div>
              </dl>
            )}
            <Confusion matrix={viewRow.metrics?.confusion_matrix} />
          </div>
        )}
      </Modal>

      <Modal
        title="Edit notes"
        open={Boolean(notesRow)}
        onClose={closeModal}
        footer={
          <>
            <button
              type="button"
              onClick={closeModal}
              className="rounded-md border border-line bg-card px-4 py-2 text-sm text-ink"
            >
              Cancel
            </button>
            <button
              type="submit"
              form="model-notes-form"
              disabled={busy}
              className="rounded-md bg-teal px-4 py-2 text-sm font-medium text-white hover:bg-teal-dark disabled:opacity-50"
            >
              {busy ? 'Saving…' : 'Save notes'}
            </button>
          </>
        }
      >
        {error && modal?.type === 'notes' && (
          <p className="mb-4 text-sm text-red-800" role="alert">
            {error}
          </p>
        )}
        <p className="mb-4 text-sm text-slate">
          Notes are for administrators. They do not change stored sklearn metrics.
        </p>
        <form id="model-notes-form" onSubmit={saveNotes}>
          <Field label="Notes">
            <textarea
              className={selectClass}
              rows={4}
              maxLength={2000}
              value={notes}
              onChange={(event) => setNotes(event.target.value)}
            />
          </Field>
        </form>
      </Modal>

      <Modal
        title="Activate model"
        open={Boolean(activateRow)}
        onClose={closeModal}
        footer={
          <>
            <button
              type="button"
              onClick={closeModal}
              className="rounded-md border border-line bg-card px-4 py-2 text-sm text-ink"
            >
              Cancel
            </button>
            <button
              type="button"
              disabled={busy}
              onClick={() => confirmActivate(activateRow)}
              className="rounded-md bg-teal px-4 py-2 text-sm font-medium text-white hover:bg-teal-dark disabled:opacity-50"
            >
              {busy ? 'Activating…' : 'Activate'}
            </button>
          </>
        }
      >
        {activateRow && (
          <p className="text-sm leading-relaxed text-slate">
            {algorithmLabel(activateRow.algorithm)} ({activateRow.version}) will become
            the ACTIVE predictor. Any currently active model is archived. Stored
            predictions keep their original model.
            {activateRow.is_synthetic_dataset
              ? ' This artefact was trained on DEMO/SYNTHETIC labels.'
              : ''}
          </p>
        )}
        {error && modal?.type === 'activate' && (
          <p className="mt-4 text-sm text-red-800" role="alert">
            {error}
          </p>
        )}
      </Modal>

      <Modal
        title="Activate selected model"
        open={activateSelectedOpen}
        onClose={closeModal}
        footer={
          <>
            <button
              type="button"
              onClick={closeModal}
              className="rounded-md border border-line bg-card px-4 py-2 text-sm text-ink"
            >
              Cancel
            </button>
            <button
              type="button"
              disabled={busy}
              onClick={confirmActivateSelected}
              className="rounded-md bg-teal px-4 py-2 text-sm font-medium text-white hover:bg-teal-dark disabled:opacity-50"
            >
              {busy ? 'Activating…' : 'Activate selected'}
            </button>
          </>
        }
      >
        <p className="text-sm leading-relaxed text-slate">
          The last evaluation winner becomes ACTIVE. Previous active models are
          archived, not deleted.
          {evaluation?.is_synthetic
            ? ' The last comparison used DEMO/SYNTHETIC labels.'
            : ''}
        </p>
        {error && modal?.type === 'activate-selected' && (
          <p className="mt-4 text-sm text-red-800" role="alert">
            {error}
          </p>
        )}
      </Modal>

      <Modal
        title="Archive model"
        open={Boolean(archiveRow)}
        onClose={closeModal}
        footer={
          <>
            <button
              type="button"
              onClick={closeModal}
              className="rounded-md border border-line bg-card px-4 py-2 text-sm text-ink"
            >
              Cancel
            </button>
            <button
              type="button"
              disabled={busy}
              onClick={() => confirmArchive(archiveRow)}
              className="rounded-md bg-red-800 px-4 py-2 text-sm font-medium text-white hover:bg-red-900 disabled:opacity-50"
            >
              {busy ? 'Archiving…' : 'Archive'}
            </button>
          </>
        }
      >
        {archiveRow && (
          <p className="text-sm leading-relaxed text-slate">
            {archiveRow.status === 'ACTIVE'
              ? 'This takes the model out of production. New classifications will use DEMO MODE until another model is activated. Stored predictions keep this model_id.'
              : 'This archives the trained artefact. It can be activated later. Stored predictions are not deleted.'}
          </p>
        )}
        {error && modal?.type === 'archive' && (
          <p className="mt-4 text-sm text-red-800" role="alert">
            {error}
          </p>
        )}
      </Modal>
    </div>
  )
}
