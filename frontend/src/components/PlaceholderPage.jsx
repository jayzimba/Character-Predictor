export default function PlaceholderPage({ title, phase, children }) {
  return (
    <div>
      <p className="text-sm font-medium text-teal">Coming in {phase}</p>
      <h1 className="mt-2 font-serif text-3xl text-ink">{title}</h1>
      <p className="mt-3 max-w-2xl text-slate">
        {children ||
          'This route is registered so the application shell can be demonstrated. The screen will be filled in a later phase without changing the URL.'}
      </p>
    </div>
  )
}
