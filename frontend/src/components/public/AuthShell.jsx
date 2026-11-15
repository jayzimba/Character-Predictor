import BrandLogo from '../BrandLogo'

const DEFAULT_POINTS = [
  'Responses stay on your account.',
  'Classification uses a trained model, not a hidden scorecard.',
  'Results are tendencies, not a medical label.',
]

export default function AuthShell({
  eyebrow,
  title,
  lede,
  image,
  imageAlt = '',
  points = DEFAULT_POINTS,
  children,
}) {
  return (
    <main className="flex flex-1 flex-col">
      <div className="grid flex-1 lg:grid-cols-2">
        <aside className="relative min-h-[18rem] self-start overflow-hidden sm:min-h-[22rem] lg:sticky lg:top-16 lg:h-[calc(100dvh-4rem)] lg:min-h-0">
          <img
            src={image}
            alt={imageAlt}
            className="animate-kenburns absolute inset-0 h-full w-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-ink/90 via-ink/50 to-ink/20" />
          <div className="relative flex h-full min-h-[18rem] flex-col justify-end px-5 py-8 sm:min-h-[22rem] sm:px-10 sm:py-12 lg:min-h-full lg:px-12 lg:py-16">
            <div className="hidden lg:block">
              <BrandLogo inverted />
            </div>
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-sand lg:mt-10">
              {eyebrow}
            </p>
            <h1 className="mt-3 max-w-md font-serif text-3xl leading-tight text-white sm:text-4xl lg:text-5xl">
              {title}
            </h1>
            <p className="mt-4 max-w-md text-sm text-white/85 sm:text-base">{lede}</p>
            <ul className="mt-8 hidden gap-3 lg:grid">
              {points.map((item) => (
                <li
                  key={item}
                  className="rounded-2xl border border-white/15 bg-white/10 px-4 py-3 text-sm text-white/90 backdrop-blur-md"
                >
                  {item}
                </li>
              ))}
            </ul>
          </div>
        </aside>
        <section className="flex items-start justify-center bg-paper px-4 py-8 sm:px-8 sm:py-12 lg:items-center lg:py-16">
          <div className="animate-scale-in w-full max-w-md rounded-[1.75rem] border border-line bg-card p-6 shadow-sm sm:p-8">
            {children}
          </div>
        </section>
      </div>
    </main>
  )
}
