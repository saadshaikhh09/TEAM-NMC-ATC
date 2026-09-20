export function scrollProgress(scrollY: number, scrollHeight: number, viewportHeight: number) {
  const scrollable = scrollHeight - viewportHeight
  if (scrollable <= 0) return 0
  return Math.min(Math.max(scrollY / scrollable, 0), 1)
}
