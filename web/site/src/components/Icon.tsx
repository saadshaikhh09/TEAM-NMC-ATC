interface IconProps {
  /** Material Symbols ligature name, e.g. "connecting_airports". */
  name: string
  className?: string
  /** Set only when the icon carries meaning no adjacent text already gives. */
  label?: string
  title?: string
}

/**
 * Material Symbols glyph.
 *
 * Icons here sit beside their own text label almost everywhere, so the default
 * is aria-hidden — a screen reader announcing "warning warning" is noise. Pass
 * `label` for the handful that stand alone.
 */
export function Icon({ name, className = '', label, title }: IconProps) {
  return (
    <span
      aria-hidden={label ? undefined : true}
      aria-label={label}
      className={`material-symbols-outlined ${className}`}
      role={label ? 'img' : undefined}
      title={title}
    >
      {name}
    </span>
  )
}
