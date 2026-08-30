export default function StatCard({ label, value, hint }) {
  return (
    <article className="rounded-xl border border-line bg-card p-5">
      <p className="text-xs font-semibold uppercase tracking-[0.14em] text-muted">{label}</p>
      <p className="mt-3 font-serif text-3xl text-ink">{value}</p>
      {hint && <p className="mt-2 text-sm text-slate">{hint}</p>}
    </article>
  )
}
