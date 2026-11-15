const TYPES = [
  { key: 'choleric', name: 'Choleric', color: '#c45c26' },
  { key: 'melancholic', name: 'Melancholic', color: '#3d4f66' },
  { key: 'phlegmatic', name: 'Phlegmatic', color: '#0f6e68' },
  { key: 'sanguine', name: 'Sanguine', color: '#b0893e' },
]

export default function MixBarList({ mix }) {
  if (!mix) {
    return null
  }

  return (
    <ul className="space-y-3">
      {TYPES.map((item) => {
        const value = mix[item.key]
        return (
          <li key={item.key}>
            <div className="flex items-center justify-between text-sm">
              <span className="text-slate">{item.name}</span>
              <span className="font-medium text-ink">{value}%</span>
            </div>
            <div className="mt-1 h-2 overflow-hidden rounded-full bg-sand">
              <div
                className="h-full rounded-full"
                style={{ width: `${Math.min(value, 100)}%`, background: item.color }}
              />
            </div>
          </li>
        )
      })}
    </ul>
  )
}
