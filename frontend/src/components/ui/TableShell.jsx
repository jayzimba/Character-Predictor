export default function TableShell({ children, className = 'mt-8' }) {
  return (
    <div className={className}>
      <p className="mb-2 text-xs text-muted sm:hidden">Swipe sideways to see every column.</p>
      <div className="overflow-x-auto overscroll-x-contain rounded-xl border border-line bg-card">
        {children}
      </div>
    </div>
  )
}
