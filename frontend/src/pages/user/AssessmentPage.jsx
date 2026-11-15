import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  fetchAssessment,
  listAssessments,
  saveAnswers,
  startAssessment,
  submitAssessment,
} from '../../api/assessments'
import { classifyAssessment } from '../../api/predictions'
import { fetchActiveQuestionnaire } from '../../api/questions'

function answersToMap(answers) {
  return Object.fromEntries(answers.map((item) => [item.question_id, item.response_value]))
}

export default function AssessmentPage() {
  const [instrument, setInstrument] = useState(null)
  const [assessment, setAssessment] = useState(null)
  const [responses, setResponses] = useState({})
  const [index, setIndex] = useState(0)
  const [consent, setConsent] = useState(false)
  const [error, setError] = useState(null)
  const [status, setStatus] = useState('loading')
  const [busy, setBusy] = useState(false)
  const [prediction, setPrediction] = useState(null)

  useEffect(() => {
    let cancelled = false

    async function load() {
      try {
        const [instrumentResponse, listResponse] = await Promise.all([
          fetchActiveQuestionnaire(),
          listAssessments(),
        ])
        if (cancelled) {
          return
        }
        const loadedInstrument = instrumentResponse.data.data
        setInstrument(loadedInstrument)
        const inProgress = (listResponse.data.data ?? []).find(
          (item) => item.status === 'IN_PROGRESS',
        )
        if (!inProgress) {
          setStatus('consent')
          return
        }
        const detail = await fetchAssessment(inProgress.id)
        if (cancelled) {
          return
        }
        const loaded = detail.data.data
        const map = answersToMap(loaded.answers)
        setAssessment(loaded)
        setResponses(map)
        const firstUnanswered = loadedInstrument.questions.findIndex(
          (item) => map[item.id] == null,
        )
        setIndex(firstUnanswered === -1 ? 0 : firstUnanswered)
        setStatus('taking')
      } catch (err) {
        if (!cancelled) {
          setError(err.response?.data?.message || 'Could not load the assessment.')
          setStatus('error')
        }
      }
    }

    load()
    return () => {
      cancelled = true
    }
  }, [])

  const questions = instrument?.questions ?? []
  const current = questions[index]
  const answeredCount = useMemo(
    () => questions.filter((item) => responses[item.id] != null).length,
    [questions, responses],
  )
  const total = questions.length
  const percent = total ? Math.round((answeredCount / total) * 100) : 0
  const complete = total > 0 && answeredCount === total

  async function handleStart(event) {
    event.preventDefault()
    setBusy(true)
    setError(null)
    try {
      const response = await startAssessment()
      setAssessment(response.data.data)
      setResponses(answersToMap(response.data.data.answers))
      setIndex(0)
      setStatus('taking')
    } catch (err) {
      setError(err.response?.data?.message || 'Could not start the assessment.')
    } finally {
      setBusy(false)
    }
  }

  async function persist(questionId, value) {
    if (!assessment) {
      return
    }
    const next = { ...responses, [questionId]: value }
    setResponses(next)
    try {
      const response = await saveAnswers(assessment.id, [
        { question_id: questionId, response_value: value },
      ])
      setAssessment(response.data.data)
    } catch (err) {
      setError(err.response?.data?.message || 'Could not save that answer.')
    }
  }

  async function handleSave() {
    if (!assessment || !current || responses[current.id] == null) {
      return
    }
    setBusy(true)
    setError(null)
    try {
      await persist(current.id, responses[current.id])
    } finally {
      setBusy(false)
    }
  }

  async function handleSubmit() {
    if (!assessment || !complete) {
      return
    }
    setBusy(true)
    setError(null)
    try {
      const response = await submitAssessment(assessment.id)
      setAssessment(response.data.data)
      setStatus('submitted')
      try {
        const classified = await classifyAssessment(response.data.data.id)
        setPrediction(classified.data.data)
      } catch (classifyError) {
        if (classifyError.response?.status !== 409) {
          setError(
            classifyError.response?.data?.message ||
              'Answers are stored. Classification could not be completed yet.'
          )
        }
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Could not submit the assessment.')
    } finally {
      setBusy(false)
    }
  }

  if (status === 'loading') {
    return <p className="text-slate">Loading the active instrument…</p>
  }

  if (status === 'error' && !instrument) {
    return (
      <p className="text-sm text-red-800" role="alert">
        {error}
      </p>
    )
  }

  if (status === 'submitted') {
    return (
      <div>
        <p className="text-sm font-medium text-teal">
          {prediction ? 'Classified' : 'Submitted'}
        </p>
        <h1 className="mt-1 font-serif text-3xl text-ink">
          {prediction
            ? `Your assessment indicates ${prediction.personality_name}`
            : 'Your answers are stored'}
        </h1>
        {prediction ? (
          <div className="mt-3 space-y-3 text-slate">
            <p>{prediction.disclaimer}</p>
            {prediction.is_demo_mode && (
              <p className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-950">
                DEMO MODE. {prediction.demo_reason}
              </p>
            )}
            <p className="text-sm">
              Confidence {Math.round(prediction.confidence * 100)}% · mix from{' '}
              {prediction.mix_source}
            </p>
          </div>
        ) : (
          <p className="mt-3 text-slate">
            This assessment is marked complete. Open the dashboard after
            classification to see a stored type and mix.
          </p>
        )}
        <div className="mt-8 flex flex-wrap gap-3">
          {prediction && (
            <Link
              to={`/app/results?assessment_id=${assessment?.id ?? prediction.assessment_id}`}
              className="inline-flex rounded-md bg-teal px-4 py-2.5 text-sm font-medium text-white hover:bg-teal-dark"
            >
              View full result
            </Link>
          )}
          <Link
            to="/app"
            className="inline-flex rounded-md border border-line bg-card px-4 py-2.5 text-sm font-medium text-ink hover:border-teal"
          >
            Back to dashboard
          </Link>
        </div>
      </div>
    )
  }

  if (status === 'consent') {
    return (
      <div>
        <p className="text-sm font-medium text-teal">Before you begin</p>
        <h1 className="mt-1 font-serif text-3xl text-ink">{instrument.name}</h1>
        <p className="mt-3 text-slate">{instrument.description}</p>
        <p className="mt-6 rounded-xl border border-line bg-sand/60 px-4 py-3 text-sm text-slate">
          {instrument.disclaimer}
        </p>
        <p className="mt-4 text-sm text-slate">
          Answers stay on your account so you can save progress. They are used
          to build numerical features for classification later, not as a
          medical record.
        </p>
        <form className="mt-8 space-y-4" onSubmit={handleStart}>
          <label className="flex items-start gap-3 text-sm text-slate">
            <input
              type="checkbox"
              className="mt-1"
              checked={consent}
              onChange={(event) => setConsent(event.target.checked)}
              required
            />
            I understand this is for education, research and personal
            development, and I consent to storing my answers.
          </label>
          {error && (
            <p className="text-sm text-red-800" role="alert">
              {error}
            </p>
          )}
          <button
            type="submit"
            disabled={!consent || busy}
            className="rounded-md bg-teal px-4 py-2.5 text-sm font-medium text-white hover:bg-teal-dark disabled:opacity-60"
          >
            {busy ? 'Starting…' : 'Start assessment'}
          </button>
        </form>
      </div>
    )
  }

  return (
    <div>
      <p className="text-sm font-medium text-teal">Question {index + 1} of {total}</p>
      <h1 className="mt-1 font-serif text-2xl text-ink sm:text-3xl">{instrument.name}</h1>
      <div className="mt-4 h-2 overflow-hidden rounded-full bg-sand">
        <div className="h-full bg-teal transition-[width] duration-200" style={{ width: `${percent}%` }} />
      </div>
      <p className="mt-2 text-sm text-slate">
        {answeredCount} saved · {percent}% complete
      </p>

      {current && (
        <section className="mt-8 rounded-xl border border-line bg-card p-4 sm:p-6">
          <p className="text-xs font-semibold uppercase tracking-[0.14em] text-muted">
            {current.category.name}
          </p>
          <h2 className="mt-3 font-serif text-xl text-ink sm:text-2xl">{current.question_text}</h2>
          <fieldset className="mt-6">
            <legend className="sr-only">Likert response</legend>
            <div className="grid grid-cols-5 gap-1 sm:gap-2">
              {instrument.likert_scale.map((option) => {
                const selected = responses[current.id] === option.value
                return (
                  <label
                    key={option.value}
                    className={`flex min-h-[4.75rem] cursor-pointer flex-col items-center justify-center rounded-md border px-1 py-2 text-center sm:min-h-0 sm:px-3 sm:py-3 ${
                      selected
                        ? 'border-teal bg-sand text-ink'
                        : 'border-line bg-paper text-slate'
                    }`}
                  >
                    <input
                      type="radio"
                      className="sr-only"
                      name={`question-${current.id}`}
                      value={option.value}
                      checked={selected}
                      onChange={() => persist(current.id, option.value)}
                    />
                    <span className="block text-sm font-medium sm:text-base">{option.value}</span>
                    <span className="mt-1 block text-[10px] leading-tight sm:text-xs">{option.label}</span>
                  </label>
                )
              })}
            </div>
          </fieldset>
        </section>
      )}

      {error && (
        <p className="mt-4 text-sm text-red-800" role="alert">
          {error}
        </p>
      )}

      <div className="sticky bottom-0 z-10 -mx-4 mt-6 grid grid-cols-2 gap-2 border-t border-line bg-paper/95 px-4 py-3 backdrop-blur sm:static sm:mx-0 sm:flex sm:flex-wrap sm:items-center sm:border-0 sm:bg-transparent sm:px-0 sm:py-0 sm:backdrop-blur-none">
        <button
          type="button"
          disabled={index === 0}
          onClick={() => setIndex((currentIndex) => currentIndex - 1)}
          className="rounded-md border border-line bg-card px-4 py-2.5 text-sm text-ink disabled:opacity-40"
        >
          Previous
        </button>
        <button
          type="button"
          disabled={index >= total - 1}
          onClick={() => setIndex((currentIndex) => currentIndex + 1)}
          className="rounded-md border border-line bg-card px-4 py-2.5 text-sm text-ink disabled:opacity-40"
        >
          Next
        </button>
        <button
          type="button"
          disabled={busy || responses[current?.id] == null}
          onClick={handleSave}
          className="rounded-md border border-line bg-card px-4 py-2.5 text-sm text-ink disabled:opacity-40"
        >
          Save progress
        </button>
        <button
          type="button"
          disabled={!complete || busy}
          onClick={handleSubmit}
          className="rounded-md bg-teal px-4 py-2.5 text-sm font-medium text-white hover:bg-teal-dark disabled:opacity-40"
        >
          {busy ? 'Submitting…' : 'Submit assessment'}
        </button>
      </div>
      <p className="mt-8 text-xs leading-relaxed text-muted">{instrument.disclaimer}</p>
    </div>
  )
}
