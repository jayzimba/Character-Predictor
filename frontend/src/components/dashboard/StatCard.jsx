export default function StatCard({ label, value, hint }) {
  return (
    <article className="hover-lift rounded-xl border border-line bg-card p-5">
      <p className="text-xs font-semibold uppercase tracking-[0.14em] text-muted">{label}</p>
      <p className="mt-3 break-words font-serif text-2xl text-ink sm:text-3xl">{value}</p>
      {hint && <p className="mt-2 text-sm text-slate">{hint}</p>}
    </article>
  )
}
