import { useEffect, useMemo, useState } from 'react'
import Field, { selectClass } from '../../components/public/Field'
import Modal from '../../components/ui/Modal'
import TableShell from '../../components/ui/TableShell'
import IconButton, {
  ChevronIcon,
  EyeIcon,
  PauseIcon,
  PencilIcon,
  PlayIcon,
  PlusIcon,
} from '../../components/ui/IconButton'
import {
  createAdminQuestion,
  fetchAdminQuestions,
  fetchQuestionOptions,
  updateAdminQuestion,
} from '../../api/questions'

const PAGE_SIZE = 10

const emptyForm = {
  question_text: '',
  category_code: '',
  personality_code: '',
  weight: '1',
  reverse_scored: false,
}

function defaultsFromOptions(options) {
  return {
    ...emptyForm,
    category_code: options.categories[0]?.code || '',
    personality_code: options.personality_types[0]?.code || '',
  }
}

function formFromRow(row) {
  return {
    question_text: row.question_text,
    category_code: row.category.code,
    personality_code: row.personality_trait?.code || '',
    weight: String(row.weight),
    reverse_scored: row.reverse_scored,
  }
}

export default function QuestionsPage() {
  const [rows, setRows] = useState([])
  const [options, setOptions] = useState({ categories: [], personality_types: [] })
  const [form, setForm] = useState(emptyForm)
  const [page, setPage] = useState(1)
  const [modal, setModal] = useState(null)
  const [error, setError] = useState(null)
  const [message, setMessage] = useState(null)
  const [busy, setBusy] = useState(false)

  const pageCount = Math.max(1, Math.ceil(rows.length / PAGE_SIZE))
  const currentPage = Math.min(page, pageCount)
  const visible = useMemo(() => {
    const start = (currentPage - 1) * PAGE_SIZE
    return rows.slice(start, start + PAGE_SIZE)
  }, [rows, currentPage])

  function loadCatalogue() {
    return fetchAdminQuestions().then((response) => setRows(response.data.data ?? []))
  }

  useEffect(() => {
    Promise.all([fetchAdminQuestions(), fetchQuestionOptions()])
      .then(([questions, optionResponse]) => {
        setRows(questions.data.data ?? [])
        setOptions(optionResponse.data.data)
      })
      .catch((err) => {
        setError(err.response?.data?.message || 'Could not load questions.')
      })
  }, [])

  function updateField(field) {
    return (event) => {
      const value =
        event.target.type === 'checkbox' ? event.target.checked : event.target.value
      setForm((current) => ({ ...current, [field]: value }))
    }
  }

  function closeModal() {
    if (!busy) {
      setModal(null)
    }
  }

  function openAdd() {
    setError(null)
    setForm(defaultsFromOptions(options))
    setModal({ type: 'add' })
  }

  function openEdit(row) {
    setError(null)
    setForm(formFromRow(row))
    setModal({ type: 'edit', row })
  }

  function openView(row) {
    setError(null)
    setModal({ type: 'view', row })
  }

  function openStatus(row) {
    setError(null)
    setModal({ type: 'status', row })
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setBusy(true)
    setError(null)
    setMessage(null)
    const payload = {
      question_text: form.question_text,
      category_code: form.category_code,
      personality_code: form.personality_code,
      weight: Number(form.weight),
      reverse_scored: form.reverse_scored,
    }
    try {
      if (modal?.type === 'edit') {
        await updateAdminQuestion(modal.row.id, payload)
        setMessage('Question updated.')
      } else {
        await createAdminQuestion(payload)
        setMessage('Question created on the active instrument.')
        setPage(Math.ceil((rows.length + 1) / PAGE_SIZE))
      }
      await loadCatalogue()
      setModal(null)
    } catch (err) {
      setError(err.response?.data?.message || 'Could not save the question.')
    } finally {
      setBusy(false)
    }
  }

  async function handleStatusConfirm() {
    const row = modal?.row
    if (!row) {
      return
    }
    const status = row.status === 'ACTIVE' ? 'INACTIVE' : 'ACTIVE'
    setBusy(true)
    setError(null)
    setMessage(null)
    try {
      await updateAdminQuestion(row.id, { status })
      setMessage(status === 'INACTIVE' ? 'Question deactivated.' : 'Question activated.')
      await loadCatalogue()
      setModal(null)
    } catch (err) {
      setError(err.response?.data?.message || 'Could not update status.')
    } finally {
      setBusy(false)
    }
  }

  const editingLocked = modal?.type === 'edit' && modal.row.scoring_locked
  const statusRow = modal?.type === 'status' ? modal.row : null
  const viewRow = modal?.type === 'view' ? modal.row : null
  const formOpen = modal?.type === 'add' || modal?.type === 'edit'
  const rangeStart = rows.length === 0 ? 0 : (currentPage - 1) * PAGE_SIZE + 1
  const rangeEnd = Math.min(currentPage * PAGE_SIZE, rows.length)

  return (
    <div>
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-teal">Instrument catalogue</p>
          <h1 className="mt-1 font-serif text-3xl text-ink">Questions</h1>
          <p className="mt-2 max-w-2xl text-slate">
            Items live in MySQL. After an answer exists, scoring fields are locked.
            Deactivate instead of deleting so past assessments stay reproducible.
          </p>
        </div>
        <button
          type="button"
          onClick={openAdd}
          className="inline-flex items-center gap-2 rounded-md bg-teal px-4 py-2.5 text-sm font-medium text-white hover:bg-teal-dark"
        >
          <PlusIcon />
          Add question
        </button>
      </div>

      {error && !modal && (
        <p className="mt-6 text-sm text-red-800" role="alert">
          {error}
        </p>
      )}
      {message && (
        <p className="mt-6 text-sm text-teal">{message}</p>
      )}

      <TableShell>
        <table className="min-w-full text-left text-sm">
          <thead className="border-b border-line text-xs uppercase tracking-wide text-muted">
            <tr>
              <th className="px-4 py-3">#</th>
              <th className="px-4 py-3">Question</th>
              <th className="px-4 py-3">Category</th>
              <th className="px-4 py-3">Trait</th>
              <th className="px-4 py-3">Weight</th>
              <th className="px-4 py-3">Reverse</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {visible.map((row) => (
              <tr key={row.id} className="border-b border-line last:border-b-0">
                <td className="px-4 py-3 text-muted">{row.display_order}</td>
                <td className="px-4 py-3 text-ink">
                  {row.question_text}
                  {row.scoring_locked && (
                    <span className="mt-1 block text-xs text-muted">
                      {row.answer_count} answer{row.answer_count === 1 ? '' : 's'} · locked
                    </span>
                  )}
                </td>
                <td className="px-4 py-3 text-slate">{row.category.name}</td>
                <td className="px-4 py-3 text-slate">{row.personality_trait?.name ?? '—'}</td>
                <td className="px-4 py-3 text-slate">{row.weight}</td>
                <td className="px-4 py-3 text-slate">{row.reverse_scored ? 'Yes' : 'No'}</td>
                <td className="px-4 py-3 text-slate">{row.status}</td>
                <td className="px-4 py-3">
                  <div className="flex justify-end gap-1">
                    <IconButton label="View question" onClick={() => openView(row)} tone="slate">
                      <EyeIcon />
                    </IconButton>
                    <IconButton
                      label={row.scoring_locked ? 'Scoring is locked' : 'Edit question'}
                      disabled={row.scoring_locked}
                      onClick={() => openEdit(row)}
                    >
                      <PencilIcon />
                    </IconButton>
                    {row.status === 'ACTIVE' ? (
                      <IconButton
                        label="Deactivate question"
                        tone="danger"
                        disabled={busy}
                        onClick={() => openStatus(row)}
                      >
                        <PauseIcon />
                      </IconButton>
                    ) : (
                      <IconButton
                        label="Activate question"
                        disabled={busy}
                        onClick={() => openStatus(row)}
                      >
                        <PlayIcon />
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
          Showing {rangeStart}–{rangeEnd} of {rows.length}
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

      <Modal
        title={modal?.type === 'edit' ? 'Edit question' : 'Add question'}
        open={formOpen}
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
              form="question-form"
              disabled={busy || Boolean(editingLocked)}
              className="rounded-md bg-teal px-4 py-2 text-sm font-medium text-white hover:bg-teal-dark disabled:opacity-50"
            >
              {busy ? 'Saving…' : modal?.type === 'edit' ? 'Save changes' : 'Add question'}
            </button>
          </>
        }
      >
        {editingLocked && (
          <p className="mb-4 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-950">
            This item already has answers. Use deactivate instead of editing.
          </p>
        )}
        {error && modal && (
          <p className="mb-4 text-sm text-red-800" role="alert">
            {error}
          </p>
        )}
        <form id="question-form" className="space-y-4" onSubmit={handleSubmit}>
          <Field label="Question text">
            <textarea
              className={selectClass}
              rows={3}
              value={form.question_text}
              onChange={updateField('question_text')}
              required
              disabled={Boolean(editingLocked)}
            />
          </Field>
          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="Category">
              <select
                className={selectClass}
                value={form.category_code}
                onChange={updateField('category_code')}
                required
                disabled={Boolean(editingLocked)}
              >
                {options.categories.map((item) => (
                  <option key={item.code} value={item.code}>
                    {item.name}
                  </option>
                ))}
              </select>
            </Field>
            <Field label="Personality trait">
              <select
                className={selectClass}
                value={form.personality_code}
                onChange={updateField('personality_code')}
                required
                disabled={Boolean(editingLocked)}
              >
                {options.personality_types.map((item) => (
                  <option key={item.code} value={item.code}>
                    {item.name}
                  </option>
                ))}
              </select>
            </Field>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="Weight">
              <input
                className={selectClass}
                type="number"
                min="0.01"
                step="0.01"
                value={form.weight}
                onChange={updateField('weight')}
                required
                disabled={Boolean(editingLocked)}
              />
            </Field>
            <label className="flex items-center gap-3 pt-7 text-sm text-slate">
              <input
                type="checkbox"
                checked={form.reverse_scored}
                onChange={updateField('reverse_scored')}
                disabled={Boolean(editingLocked)}
              />
              Reverse scored
            </label>
          </div>
        </form>
      </Modal>

      <Modal
        title="Question details"
        open={Boolean(viewRow)}
        onClose={closeModal}
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
          <dl className="space-y-3 text-sm">
            <div>
              <dt className="text-muted">Wording</dt>
              <dd className="mt-1 text-ink">{viewRow.question_text}</dd>
            </div>
            <div className="grid gap-3 sm:grid-cols-2">
              <div>
                <dt className="text-muted">Category</dt>
                <dd className="mt-1 text-ink">{viewRow.category.name}</dd>
              </div>
              <div>
                <dt className="text-muted">Trait</dt>
                <dd className="mt-1 text-ink">{viewRow.personality_trait?.name ?? '—'}</dd>
              </div>
              <div>
                <dt className="text-muted">Weight</dt>
                <dd className="mt-1 text-ink">{viewRow.weight}</dd>
              </div>
              <div>
                <dt className="text-muted">Reverse scored</dt>
                <dd className="mt-1 text-ink">{viewRow.reverse_scored ? 'Yes' : 'No'}</dd>
              </div>
              <div>
                <dt className="text-muted">Status</dt>
                <dd className="mt-1 text-ink">{viewRow.status}</dd>
              </div>
              <div>
                <dt className="text-muted">Answers</dt>
                <dd className="mt-1 text-ink">
                  {viewRow.answer_count}
                  {viewRow.scoring_locked ? ' · scoring locked' : ''}
                </dd>
              </div>
            </div>
          </dl>
        )}
      </Modal>

      <Modal
        title={statusRow?.status === 'ACTIVE' ? 'Deactivate question' : 'Activate question'}
        open={Boolean(statusRow)}
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
              onClick={handleStatusConfirm}
              className={`rounded-md px-4 py-2 text-sm font-medium text-white disabled:opacity-50 ${
                statusRow?.status === 'ACTIVE' ? 'bg-red-800 hover:bg-red-900' : 'bg-teal hover:bg-teal-dark'
              }`}
            >
              {busy
                ? 'Saving…'
                : statusRow?.status === 'ACTIVE'
                  ? 'Deactivate'
                  : 'Activate'}
            </button>
          </>
        }
      >
        {statusRow && (
          <p className="text-sm leading-relaxed text-slate">
            {statusRow.status === 'ACTIVE'
              ? 'This hides the item from new assessments. Existing answers stay stored so past results stay reproducible.'
              : 'This returns the item to the active instrument for new assessments.'}
          </p>
        )}
        {error && modal?.type === 'status' && (
          <p className="mt-4 text-sm text-red-800" role="alert">
            {error}
          </p>
        )}
      </Modal>
    </div>
  )
}
