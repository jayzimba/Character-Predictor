export default function AuthShell({ eyebrow, title, lede, children }) {
  return (
    <main className="mx-auto grid min-h-[calc(100vh-73px)] max-w-6xl items-center gap-12 px-6 py-12 lg:grid-cols-2">
      <section className="max-w-lg">
        <p className="text-sm font-medium text-teal">{eyebrow}</p>
        <h1 className="mt-3 font-serif text-4xl leading-tight text-ink">{title}</h1>
        <p className="mt-4 text-slate">{lede}</p>
        <ul className="mt-8 space-y-3 text-sm text-slate">
          <li>Responses stay on your account.</li>
          <li>Classification uses a trained model, not a hidden scorecard.</li>
          <li>Results are tendencies, not a medical label.</li>
        </ul>
      </section>
      <section className="rounded-2xl border border-line bg-card p-8 shadow-sm">
        {children}
      </section>
    </main>
  )
}
