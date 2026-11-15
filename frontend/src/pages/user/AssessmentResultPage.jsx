import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import MixBarList from '../../components/dashboard/MixBarList'
import PersonalityMixChart from '../../components/dashboard/PersonalityMixChart'
import { fetchLatestResult, fetchResult } from '../../api/results'

function formatDate(value) {
  if (!value) {
    return 'Date not stored'
  }
  return new Intl.DateTimeFormat('en-GB', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  }).format(new Date(value))
}

function formatConfidence(score) {
  if (score == null) {
    return '—'
  }
  return `${Math.round(score * 100)}%`
}

function summaryText(result) {
  const mix = result.personality_mix
  const type = result.personality
  const lines = [
    'Personality Classification Using Data Mining',
    'Educational result — not a clinical psychological diagnosis',
    '',
    result.headline,
    `Assessment date: ${formatDate(result.completed_at)}`,
    `Confidence: ${formatConfidence(result.confidence)}`,
    `Mix source: ${result.mix_source}`,
    result.is_demo_mode ? `DEMO MODE: ${result.demo_reason}` : 'DEMO MODE: no',
    '',
    'Personality mix (stored percentages)',
    `Choleric: ${mix.choleric}%`,
    `Melancholic: ${mix.melancholic}%`,
    `Phlegmatic: ${mix.phlegmatic}%`,
    `Sanguine: ${mix.sanguine}%`,
    '',
    type.tagline,
    '',
    type.description,
    '',
    'Strengths',
    ...type.strengths.map((item) => `- ${item}`),
    '',
    'Development areas',
    ...type.development_areas.map((item) => `- ${item}`),
    '',
    `Communication: ${type.communication_style}`,
    `Work style: ${type.work_style}`,
    `Career environments: ${type.career_environments}`,
    '',
    'Development notes',
    type.development_suggestions,
    '',
    result.disclaimer,
  ]
  return `${lines.join('\n')}\n`
}

export default function AssessmentResultPage() {
  const [searchParams] = useSearchParams()
  const assessmentId = searchParams.get('assessment_id')
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [empty, setEmpty] = useState(false)

  useEffect(() => {
    let cancelled = false
    const request = assessmentId
      ? fetchResult(assessmentId)
      : fetchLatestResult()

    request
      .then((response) => {
        if (!cancelled) {
          setResult(response.data.data)
          setEmpty(false)
          setError(null)
        }
      })
      .catch((err) => {
        if (cancelled) {
          return
        }
        if (err.response?.status === 404) {
          setEmpty(true)
          setResult(null)
          setError(null)
          return
        }
        setError(err.response?.data?.message || 'Could not load the result.')
      })

    return () => {
      cancelled = true
    }
  }, [assessmentId])

  function handleDownload() {
    if (!result) {
      return
    }
    const blob = new Blob([summaryText(result)], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `temperament-result-${result.assessment_id}.txt`
    link.click()
    URL.revokeObjectURL(url)
  }

  if (error) {
    return (
      <p className="text-sm text-red-800" role="alert">
        {error}
      </p>
    )
  }

  if (empty) {
    return (
      <div>
        <p className="text-sm font-medium text-teal">Results</p>
        <h1 className="mt-1 font-serif text-3xl text-ink">No stored result yet</h1>
        <p className="mt-3 text-slate">
          This page stays empty until a completed assessment is classified. The
          mix is never invented here.
        </p>
        <Link
          to="/app/assessment"
          className="mt-8 inline-flex rounded-md bg-teal px-4 py-2.5 text-sm font-medium text-white hover:bg-teal-dark"
        >
          Take assessment
        </Link>
      </div>
    )
  }

  if (!result) {
    return <p className="text-slate">Loading your stored result…</p>
  }

  const type = result.personality

  return (
    <div id="result-print">
      <div className="flex flex-wrap items-start justify-between gap-4 print:hidden">
        <div>
          <p className="text-sm font-medium text-teal">Personality result</p>
          <h1 className="mt-1 font-serif text-2xl text-ink sm:text-3xl">{result.headline}</h1>
          <p className="mt-2 max-w-2xl text-slate">{result.disclaimer}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => window.print()}
            className="rounded-md border border-line bg-card px-4 py-2 text-sm text-ink hover:border-teal"
          >
            Print
          </button>
          <button
            type="button"
            onClick={handleDownload}
            className="rounded-md bg-teal px-4 py-2 text-sm font-medium text-white hover:bg-teal-dark"
          >
            Download summary
          </button>
        </div>
      </div>

      {result.is_demo_mode && (
        <p className="mt-6 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-950">
          DEMO MODE. {result.demo_reason}
        </p>
      )}

      <section className="mt-8 grid gap-4 sm:grid-cols-3">
        <article className="rounded-xl border border-line bg-card p-5">
          <p className="text-xs uppercase tracking-[0.14em] text-muted">Indicated type</p>
          <p className="mt-2 font-serif text-2xl text-ink">{type.name}</p>
          <p className="mt-1 text-sm text-slate">{type.tagline}</p>
        </article>
        <article className="rounded-xl border border-line bg-card p-5">
          <p className="text-xs uppercase tracking-[0.14em] text-muted">Confidence</p>
          <p className="mt-2 font-serif text-2xl text-ink">
            {formatConfidence(result.confidence)}
          </p>
          <p className="mt-1 text-sm text-slate">
            Mix from {result.mix_source}
            {result.algorithm ? ` · ${result.algorithm.replaceAll('_', ' ')}` : ''}
          </p>
        </article>
        <article className="rounded-xl border border-line bg-card p-5">
          <p className="text-xs uppercase tracking-[0.14em] text-muted">Assessment date</p>
          <p className="mt-2 font-serif text-2xl text-ink">{formatDate(result.completed_at)}</p>
          <p className="mt-1 text-sm text-slate">Assessment #{result.assessment_id}</p>
        </article>
      </section>

      <section className="mt-8 rounded-xl border border-line bg-card p-6">
        <h2 className="font-serif text-2xl text-ink">Personality mix</h2>
        <p className="mt-1 text-sm text-slate">
          Percentages are the stored model output. They are not estimated on
          this page.
        </p>
        <div className="mt-6">
          <PersonalityMixChart mix={result.personality_mix} />
        </div>
        <div className="mt-8">
          <MixBarList mix={result.personality_mix} />
        </div>
      </section>

      <section className="mt-8 rounded-xl border border-line bg-card p-6">
        <h2 className="font-serif text-2xl text-ink">{type.name}</h2>
        <p className="mt-3 leading-relaxed text-slate">{type.description}</p>
        <p className="mt-4 text-sm text-slate">{type.characteristics.join(' · ')}</p>
      </section>

      <section className="mt-8 grid gap-6 md:grid-cols-2">
        <article className="rounded-xl border border-line bg-card p-6">
          <h2 className="font-serif text-xl text-ink">Strengths</h2>
          <ul className="mt-4 list-disc space-y-2 pl-5 text-sm text-slate">
            {type.strengths.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </article>
        <article className="rounded-xl border border-line bg-card p-6">
          <h2 className="font-serif text-xl text-ink">Development areas</h2>
          <ul className="mt-4 list-disc space-y-2 pl-5 text-sm text-slate">
            {type.development_areas.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </article>
      </section>

      <section className="mt-8 grid gap-6 md:grid-cols-2">
        <article className="rounded-xl border border-line bg-card p-6">
          <h2 className="font-serif text-xl text-ink">Communication and work</h2>
          <p className="mt-4 text-sm leading-relaxed text-slate">{type.communication_style}</p>
          <p className="mt-3 text-sm leading-relaxed text-slate">{type.work_style}</p>
        </article>
        <article className="rounded-xl border border-line bg-card p-6">
          <h2 className="font-serif text-xl text-ink">Career environments</h2>
          <p className="mt-4 text-sm leading-relaxed text-slate">{type.career_environments}</p>
        </article>
      </section>

      <section className="mt-8 rounded-xl border border-line bg-card p-6">
        <h2 className="font-serif text-2xl text-ink">Development notes</h2>
        <p className="mt-3 leading-relaxed text-slate">{type.development_suggestions}</p>
      </section>

      <p className="mt-8 text-xs leading-relaxed text-muted">{type.disclaimer}</p>

      <div className="mt-8 flex flex-wrap gap-3 print:hidden">
        <Link
          to="/app"
          className="rounded-md border border-line bg-card px-4 py-2 text-sm text-ink hover:border-teal"
        >
          Back to dashboard
        </Link>
        <Link
          to="/app/assessment"
          className="rounded-md bg-teal px-4 py-2 text-sm font-medium text-white hover:bg-teal-dark"
        >
          Take another assessment
        </Link>
      </div>
    </div>
  )
}
