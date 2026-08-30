export default function AboutPage() {
  return (
    <main className="mx-auto max-w-3xl px-6 py-16">
      <p className="text-sm font-medium text-teal">About the project</p>
      <h1 className="mt-2 font-serif text-4xl text-ink">Personality classification as a research system</h1>
      <p className="mt-4 text-lg text-slate">
        Temperament Lab is a university final-year platform that collects
        behavioural questionnaire answers, turns them into numerical features,
        and classifies them into four educational temperament types.
      </p>
      <section className="mt-12 space-y-8 text-sm leading-relaxed text-slate">
        <div>
          <h2 className="font-serif text-2xl text-ink">What the system does</h2>
          <p className="mt-3">
            Participants complete a versioned Likert instrument stored in MySQL.
            Answers are aggregated into category scores — leadership, patience,
            sociability and similar traits. Those scores become the feature
            vector for Decision Tree, Naive Bayes and K-Nearest Neighbours.
          </p>
        </div>
        <div>
          <h2 className="font-serif text-2xl text-ink">What it does not do</h2>
          <p className="mt-3">
            The four labels — Choleric, Melancholic, Phlegmatic and Sanguine —
            are a simplified educational scheme. The platform does not offer a
            clinical psychological diagnosis, and result copy is written as
            “your assessment indicates…”, not as a certainty about a person.
          </p>
        </div>
        <div>
          <h2 className="font-serif text-2xl text-ink">How models are judged</h2>
          <p className="mt-3">
            Accuracy, precision, recall and F1 come from evaluation on a held-out
            split. They are never invented for a report. If a synthetic training
            set is used while labelled data is scarce, that work is labelled DEMO
            and is not presented as a research finding.
          </p>
        </div>
      </section>
      <p className="mt-12 border-t border-line pt-8 text-sm leading-relaxed text-muted">
        This assessment is intended for educational, research and
        personal-development purposes and should not be considered a clinical
        psychological diagnosis.
      </p>
    </main>
  )
}
