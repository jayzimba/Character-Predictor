import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'

const COLORS = {
  Choleric: '#c45c26',
  Melancholic: '#3d4f66',
  Phlegmatic: '#0f6e68',
  Sanguine: '#b0893e',
}

function MixTooltip({ active, payload }) {
  if (!active || !payload?.length) {
    return null
  }
  const item = payload[0]
  return (
    <div className="rounded-md border border-line bg-card px-3 py-2 text-sm text-ink shadow-sm">
      {item.name}: {item.value}%
    </div>
  )
}

export default function PersonalityMixChart({ mix }) {
  if (!mix) {
    return (
      <div className="flex h-64 flex-col items-center justify-center rounded-xl border border-dashed border-line bg-paper px-6 text-center">
        <p className="font-serif text-xl text-ink">No classification yet</p>
        <p className="mt-2 max-w-sm text-sm text-slate">
          A doughnut chart will appear here after a completed assessment is
          classified. Percentages will come from the stored model output, not
          from a placeholder mix.
        </p>
      </div>
    )
  }

  const data = [
    { name: 'Choleric', value: mix.choleric },
    { name: 'Melancholic', value: mix.melancholic },
    { name: 'Phlegmatic', value: mix.phlegmatic },
    { name: 'Sanguine', value: mix.sanguine },
  ]

  return (
    <div className="grid gap-6 md:grid-cols-[220px_1fr]">
      <div className="h-56">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              dataKey="value"
              nameKey="name"
              innerRadius={58}
              outerRadius={84}
              paddingAngle={2}
              stroke="none"
            >
              {data.map((item) => (
                <Cell key={item.name} fill={COLORS[item.name]} />
              ))}
            </Pie>
            <Tooltip content={<MixTooltip />} />
          </PieChart>
        </ResponsiveContainer>
      </div>
      <ul className="space-y-3 self-center text-sm">
        {data.map((item) => (
          <li key={item.name} className="flex items-center justify-between gap-4">
            <span className="flex items-center gap-2 text-slate">
              <span
                className="inline-block h-2.5 w-2.5 rounded-full"
                style={{ background: COLORS[item.name] }}
                aria-hidden="true"
              />
              {item.name}
            </span>
            <span className="font-medium text-ink">{item.value}%</span>
          </li>
        ))}
      </ul>
    </div>
  )
}
