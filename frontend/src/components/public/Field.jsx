export default function Field({
  label,
  type = 'text',
  value,
  onChange,
  required,
  autoComplete,
  children,
}) {
  const controlClass =
    'mt-1 min-h-11 w-full rounded-md border border-line bg-paper px-3 py-2.5 text-base text-ink outline-none focus:border-teal sm:text-sm'

  return (
    <label className="block text-sm text-slate">
      {label}
      {children ? (
        <span className="block">{children}</span>
      ) : (
        <input
          className={controlClass}
          type={type}
          value={value}
          onChange={onChange}
          required={required}
          autoComplete={autoComplete}
        />
      )}
    </label>
  )
}

export const selectClass =
  'mt-1 min-h-11 w-full rounded-md border border-line bg-paper px-3 py-2.5 text-base text-ink outline-none focus:border-teal sm:text-sm'
