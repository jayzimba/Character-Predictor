import { useEffect, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import apiClient from '../../api/client'
import Reveal from '../../components/Reveal'
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

const TYPE_IMAGES = {
  CHOLERIC: '/landing/choleric.jpg',
  MELANCHOLIC: '/landing/melancholic.jpg',
  PHLEGMATIC: '/landing/phlegmatic.jpg',
  SANGUINE: '/landing/sanguine.jpg',
}

const fallbackTypes = [
  { code: 'CHOLERIC', name: 'Choleric', tagline: 'Direct, decisive, and oriented toward goals.' },
  { code: 'MELANCHOLIC', name: 'Melancholic', tagline: 'Thoughtful, organised, and attentive to quality.' },
  { code: 'PHLEGMATIC', name: 'Phlegmatic', tagline: 'Calm, dependable, and steady in a group.' },
  { code: 'SANGUINE', name: 'Sanguine', tagline: 'Outgoing, expressive, and energised by people.' },
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

  const catalogue = types.length ? types : fallbackTypes

  return (
    <main>
      <section className="relative min-h-0 overflow-hidden bg-ink md:min-h-[88vh]">
        <img
          src="/landing/hero.jpg"
          alt=""
          fetchPriority="high"
          decoding="async"
          className="animate-kenburns absolute inset-0 h-full w-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-ink via-ink/55 to-ink/15" />
        <div className="relative mx-auto flex min-h-0 max-w-6xl flex-col justify-end px-4 pb-14 pt-24 sm:px-6 md:min-h-[88vh] md:pb-20 md:pt-28">
          <p className="animate-fade-up text-xs font-semibold uppercase tracking-[0.22em] text-sand">
            Temperament classification research
          </p>
          <h1
            className="animate-fade-up mt-4 max-w-3xl font-serif text-4xl leading-[1.05] text-white sm:text-5xl md:text-7xl"
            style={{ animationDelay: '80ms' }}
          >
            Discover your personality through data
          </h1>
          <p
            className="animate-fade-up mt-5 max-w-xl text-base text-white/85 sm:text-lg"
            style={{ animationDelay: '160ms' }}
          >
            An intelligent classification platform that turns Likert answers into
            features, then a trained model — not a hidden scorecard.
          </p>
          <div
            className="animate-fade-up mt-8 flex flex-col gap-3 sm:flex-row"
            style={{ animationDelay: '240ms' }}
          >
            <Link
              to={assessmentPath}
              className="btn-press inline-flex justify-center rounded-full bg-teal px-6 py-3 text-sm font-medium text-white hover:bg-teal-dark"
            >
              Take assessment
            </Link>
            <a
              href="#how-it-works"
              className="btn-press inline-flex justify-center rounded-full border border-white/30 bg-white/10 px-6 py-3 text-sm font-medium text-white backdrop-blur hover:bg-white/20"
            >
              How it works
            </a>
          </div>
          <dl className="mt-12 grid gap-3 sm:grid-cols-3">
            {[
              ['Primary type', 'One of four temperaments'],
              ['Mix', 'Percentages from the model'],
              ['Guidance', 'Strengths and development'],
            ].map(([label, value], index) => (
              <div
                key={label}
                className="animate-fade-up rounded-2xl border border-white/15 bg-white/10 px-4 py-4 backdrop-blur-md"
                style={{ animationDelay: `${320 + index * 90}ms` }}
              >
                <dt className="text-xs uppercase tracking-[0.16em] text-white/70">{label}</dt>
                <dd className="mt-2 text-sm font-medium text-white">{value}</dd>
              </div>
            ))}
          </dl>
          <p
            className="animate-fade-up mt-6 max-w-2xl text-xs leading-relaxed text-white/70"
            style={{ animationDelay: '620ms' }}
          >
            Results use cautious language: “Your assessment indicates…”, never
            “You definitely are…”. This is educational, not a clinical diagnosis.
          </p>
        </div>
      </section>

      <section id="how-it-works" className="scroll-mt-24">
        <div className="mx-auto grid max-w-6xl items-center gap-10 px-4 py-16 sm:px-6 md:py-24 lg:grid-cols-[1.05fr_0.95fr]">
          <Reveal className="overflow-hidden rounded-[2rem] border border-line">
            <img
              src="/landing/research.jpg"
              alt="A research workstation with abstract model visualisations"
              loading="lazy"
              decoding="async"
              className="h-full min-h-[22rem] w-full object-cover object-[center_65%] transition duration-700 hover:scale-[1.03]"
            />
          </Reveal>
          <Reveal delay={80}>
            <p className="text-sm font-medium text-teal">How it works</p>
            <h2 className="mt-2 font-serif text-3xl text-ink md:text-4xl">
              From Likert answers to a class label
            </h2>
            <ol className="mt-8 space-y-6">
              {STEPS.map((item) => (
                <li key={item.step} className="flex gap-4">
                  <span className="mt-0.5 font-serif text-2xl text-teal">{item.step}</span>
                  <div>
                    <h3 className="font-serif text-xl text-ink">{item.title}</h3>
                    <p className="mt-2 text-sm leading-relaxed text-slate">{item.body}</p>
                  </div>
                </li>
              ))}
            </ol>
          </Reveal>
        </div>
      </section>

      <section className="bg-card">
        <div className="mx-auto max-w-6xl px-4 py-16 sm:px-6 md:py-24">
          <div className="flex flex-wrap items-end justify-between gap-4">
            <div>
              <p className="text-sm font-medium text-teal">Four temperaments</p>
              <h2 className="mt-2 font-serif text-3xl text-ink md:text-4xl">
                Educational classes, not diagnoses
              </h2>
            </div>
            <Link to="/personality-types" className="text-sm font-medium text-teal hover:text-teal-dark">
              Read full descriptions
            </Link>
          </div>
          <div className="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {catalogue.map((item, index) => (
              <Reveal
                key={item.code}
                as="article"
                delay={index * 90}
                className="group hover-lift relative min-h-[22rem] overflow-hidden rounded-[1.75rem] border border-line"
              >
                <img
                  src={TYPE_IMAGES[item.code] || '/landing/hero.jpg'}
                  alt=""
                  loading="lazy"
                  decoding="async"
                  className="absolute inset-0 h-full w-full object-cover transition duration-500 group-hover:scale-105"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-ink/85 via-ink/25 to-transparent" />
                <div className="absolute inset-x-0 bottom-0 p-5">
                  <h3 className="font-serif text-2xl text-white">{item.name}</h3>
                  <p className="mt-2 text-sm text-white/85">{item.tagline}</p>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      <section>
        <div className="mx-auto max-w-6xl px-4 py-16 sm:px-6 md:py-24">
          <p className="text-sm font-medium text-teal">Why a platform</p>
          <h2 className="mt-2 max-w-2xl font-serif text-3xl text-ink md:text-4xl">
            Faster, more consistent assessment
          </h2>
          <div className="mt-10 grid gap-5 md:grid-cols-3">
            <Reveal className="relative min-h-[22rem] overflow-hidden rounded-[1.75rem] md:col-span-3">
              <img
                src="/landing/benefits.jpg"
                alt=""
                loading="lazy"
                decoding="async"
                className="absolute inset-0 h-full w-full object-cover object-center"
              />
              <div className="absolute inset-0 bg-gradient-to-r from-ink/80 via-ink/45 to-ink/10" />
              <div className="absolute inset-y-0 left-0 flex max-w-lg flex-col justify-end p-7 md:justify-center md:p-10">
                <h3 className="font-serif text-2xl text-white md:text-3xl">{BENEFITS[0].title}</h3>
                <p className="mt-3 text-sm leading-relaxed text-white/85">{BENEFITS[0].body}</p>
              </div>
            </Reveal>
            {BENEFITS.slice(1).map((item, index) => (
              <Reveal
                key={item.title}
                as="article"
                delay={120 + index * 80}
                className="hover-lift rounded-[1.75rem] border border-line bg-card p-7"
              >
                <h3 className="font-serif text-2xl text-ink">{item.title}</h3>
                <p className="mt-3 text-sm leading-relaxed text-slate">{item.body}</p>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      <section className="bg-card">
        <div className="mx-auto grid max-w-6xl items-center gap-10 px-4 py-16 sm:px-6 md:py-24 lg:grid-cols-2 lg:gap-16">
          <Reveal>
            <p className="text-sm font-medium text-teal">Data mining</p>
            <h2 className="mt-2 font-serif text-3xl text-ink md:text-4xl">
              Supervised classification on behavioural features
            </h2>
            <p className="mt-4 text-slate">
              The system treats personality assignment as a four-class
              classification problem. Category scores are the features.
              Choleric, Melancholic, Phlegmatic and Sanguine are the labels.
            </p>
            <ul className="mt-8 space-y-4 text-sm text-slate">
              <li>
                <span className="font-medium text-ink">Decision Tree</span> — splits
                that a report can interpret.
              </li>
              <li>
                <span className="font-medium text-ink">Naive Bayes</span> — a
                probabilistic baseline.
              </li>
              <li>
                <span className="font-medium text-ink">K-Nearest Neighbours</span> —
                instance-based comparison, with scaled features.
              </li>
            </ul>
            <p className="mt-6 text-sm text-muted">
              Metrics always come from evaluation on held-out data. Synthetic
              training sets, if used, are labelled DEMO and are not research findings.
            </p>
          </Reveal>
          <Reveal delay={100} className="overflow-hidden rounded-[2rem] border border-line">
            <img
              src="/landing/hero.jpg"
              alt="Abstract four-colour classification rings on a studio display"
              className="h-full min-h-[18rem] w-full object-cover transition duration-700 hover:scale-[1.03]"
            />
          </Reveal>
        </div>
      </section>

      <section className="relative overflow-hidden">
        <img src="/landing/cta.jpg" alt="" className="absolute inset-0 h-full w-full object-cover" />
        <div className="absolute inset-0 bg-ink/65" />
        <div className="relative mx-auto max-w-3xl px-4 py-24 text-center sm:px-6 md:py-32">
          <Reveal>
            <h2 className="font-serif text-3xl text-white md:text-5xl">Start with a short assessment</h2>
            <p className="mx-auto mt-4 max-w-xl text-white/85">
              Create an account, give consent, and work through the questionnaire
              at your own pace. You can save progress before you submit.
            </p>
            <Link
              to={assessmentPath}
              className="btn-press mt-8 inline-flex rounded-full bg-teal px-7 py-3 text-sm font-medium text-white hover:bg-teal-dark"
            >
              Take assessment
            </Link>
          </Reveal>
        </div>
      </section>
    </main>
  )
}
