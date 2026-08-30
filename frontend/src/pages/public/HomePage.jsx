import { useEffect, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import apiClient from '../../api/client'
import { useAuth } from '../../context/AuthContext'

const STEPS = [
  {
    step: '01',
    title: 'Answer a structured questionnaire',
    body: 'Likert items are stored in the database and grouped into behavioural categories such as leadership, patience and sociability.',
  },
  {
    step: '02',
    title: 'Turn answers into features',
    body: 'Responses become numerical category scores. That is feature engineering — not the final personality label.',
  },
  {
    step: '03',
    title: 'Classify with a trained model',
    body: 'Decision Tree, Naive Bayes and KNN are trained on the same split. The active model predicts a temperament class.',
  },
]

const BENEFITS = [
  {
    title: 'Consistent collection',
    body: 'Every participant sees the same versioned instrument, so results can be compared over time.',
  },
  {
    title: 'Explainable algorithms',
    body: 'Classical classifiers are used so accuracy, precision, recall and F1 can be reported honestly.',
  },
  {
    title: 'Separate scoring from ML',
    body: 'Questionnaire totals are inputs. The class comes from a persisted scikit-learn model, not if-statements.',
  },
  {
    title: 'Role-aware access',
    body: 'Users see only their assessments. Administrators train models and review aggregates, not other people’s answers.',
  },
]

export default function HomePage() {
  const { user } = useAuth()
  const location = useLocation()
  const [types, setTypes] = useState([])
  const assessmentPath = user ? '/app/assessment' : '/register'

  useEffect(() => {
    apiClient
      .get('/personality-types')
      .then((response) => setTypes(response.data.data ?? []))
      .catch(() => setTypes([]))
  }, [])

  useEffect(() => {
    if (location.hash !== '#how-it-works') {
      return
    }
    document.getElementById('how-it-works')?.scrollIntoView({ behavior: 'smooth' })
  }, [location.hash])

  return (
    <main>
      <section className="border-b border-line bg-card">
        <div className="mx-auto grid max-w-6xl items-center gap-12 px-6 py-20 lg:grid-cols-[1.15fr_0.85fr]">
          <div>
            <p className="text-sm font-medium text-teal">Temperament classification research</p>
            <h1 className="mt-4 font-serif text-4xl leading-tight text-ink md:text-6xl">
              Discover Your Personality Through Data
            </h1>
            <p className="mt-5 max-w-xl text-lg text-slate">
              An intelligent personality classification platform powered by data
              mining and machine learning.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link
                to={assessmentPath}
                className="rounded-md bg-teal px-5 py-2.5 text-sm font-medium text-white hover:bg-teal-dark"
              >
                Take Assessment
              </Link>
              <a
                href="#how-it-works"
                className="rounded-md border border-line bg-paper px-5 py-2.5 text-sm font-medium text-ink"
              >
                Learn More
              </a>
            </div>
          </div>
          <aside className="rounded-2xl border border-line bg-paper p-6">
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-muted">
              What you receive
            </p>
            <dl className="mt-5 space-y-4 text-sm">
              <div className="flex justify-between gap-4 border-b border-line pb-3">
                <dt className="text-slate">Primary type</dt>
                <dd className="font-medium text-ink">One of four temperaments</dd>
              </div>
              <div className="flex justify-between gap-4 border-b border-line pb-3">
                <dt className="text-slate">Mix</dt>
                <dd className="font-medium text-ink">Percentages from the model</dd>
              </div>
              <div className="flex justify-between gap-4">
                <dt className="text-slate">Guidance</dt>
                <dd className="font-medium text-ink">Strengths and development</dd>
              </div>
            </dl>
            <p className="mt-6 text-xs leading-relaxed text-muted">
              Language on results pages is cautious: “Your assessment indicates…”,
              never “You definitely are…”.
            </p>
          </aside>
        </div>
      </section>

      <section id="how-it-works" className="scroll-mt-24">
        <div className="mx-auto max-w-6xl px-6 py-20">
          <p className="text-sm font-medium text-teal">How it works</p>
          <h2 className="mt-2 font-serif text-3xl text-ink">From Likert answers to a class label</h2>
          <div className="mt-10 grid gap-6 md:grid-cols-3">
            {STEPS.map((item) => (
              <article key={item.step} className="rounded-xl border border-line bg-card p-6">
                <p className="text-xs font-semibold tracking-[0.16em] text-teal">{item.step}</p>
                <h3 className="mt-3 font-serif text-xl text-ink">{item.title}</h3>
                <p className="mt-3 text-sm leading-relaxed text-slate">{item.body}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="border-y border-line bg-card">
        <div className="mx-auto max-w-6xl px-6 py-20">
          <div className="flex flex-wrap items-end justify-between gap-4">
            <div>
              <p className="text-sm font-medium text-teal">Four temperaments</p>
              <h2 className="mt-2 font-serif text-3xl text-ink">Educational classes, not diagnoses</h2>
            </div>
            <Link to="/personality-types" className="text-sm font-medium text-teal">
              Read full descriptions
            </Link>
          </div>
          <div className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {(types.length ? types : fallbackTypes).map((item) => (
              <article key={item.code} className="rounded-xl border border-line bg-paper p-5">
                <h3 className="font-serif text-xl text-ink">{item.name}</h3>
                <p className="mt-2 text-sm text-slate">{item.tagline}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section>
        <div className="mx-auto max-w-6xl px-6 py-20">
          <p className="text-sm font-medium text-teal">Why a platform</p>
          <h2 className="mt-2 font-serif text-3xl text-ink">Faster, more consistent assessment</h2>
          <div className="mt-10 grid gap-6 md:grid-cols-2">
            {BENEFITS.map((item) => (
              <article key={item.title} className="rounded-xl border border-line bg-card p-6">
                <h3 className="font-serif text-xl text-ink">{item.title}</h3>
                <p className="mt-3 text-sm leading-relaxed text-slate">{item.body}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="border-y border-line bg-card">
        <div className="mx-auto max-w-6xl px-6 py-20 lg:grid lg:grid-cols-2 lg:gap-16">
          <div>
            <p className="text-sm font-medium text-teal">Data mining</p>
            <h2 className="mt-2 font-serif text-3xl text-ink">
              Supervised classification on behavioural features
            </h2>
            <p className="mt-4 text-slate">
              The system treats personality assignment as a four-class
              classification problem. Category scores are the features.
              Choleric, Melancholic, Phlegmatic and Sanguine are the labels.
            </p>
          </div>
          <div className="mt-8 space-y-4 text-sm text-slate lg:mt-10">
            <p>
              <span className="font-medium text-ink">Decision Tree</span> — splits
              that a report can interpret.
            </p>
            <p>
              <span className="font-medium text-ink">Naive Bayes</span> — a
              probabilistic baseline.
            </p>
            <p>
              <span className="font-medium text-ink">K-Nearest Neighbours</span> —
              instance-based comparison, with scaled features.
            </p>
            <p className="text-muted">
              Metrics always come from evaluation on held-out data. Synthetic
              training sets, if used, are labelled DEMO and are not research findings.
            </p>
          </div>
        </div>
      </section>

      <section>
        <div className="mx-auto max-w-6xl px-6 py-20 text-center">
          <h2 className="font-serif text-3xl text-ink">Start with a short assessment</h2>
          <p className="mx-auto mt-3 max-w-xl text-slate">
            Create an account, give consent, and work through the questionnaire
            at your own pace. You can save progress before you submit.
          </p>
          <Link
            to={assessmentPath}
            className="mt-8 inline-flex rounded-md bg-teal px-6 py-2.5 text-sm font-medium text-white hover:bg-teal-dark"
          >
            Take Assessment
          </Link>
        </div>
      </section>
    </main>
  )
}

const fallbackTypes = [
  { code: 'CHOLERIC', name: 'Choleric', tagline: 'Direct, decisive, and oriented toward goals.' },
  { code: 'MELANCHOLIC', name: 'Melancholic', tagline: 'Thoughtful, organised, and attentive to quality.' },
  { code: 'PHLEGMATIC', name: 'Phlegmatic', tagline: 'Calm, dependable, and steady in a group.' },
  { code: 'SANGUINE', name: 'Sanguine', tagline: 'Outgoing, expressive, and energised by people.' },
]
