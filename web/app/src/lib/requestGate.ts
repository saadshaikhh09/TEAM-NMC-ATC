export function createRequestGate() {
  let latest = 0
  return {
    next: () => ++latest,
    isCurrent: (request: number) => request === latest,
    cancel: () => { latest += 1 },
  }
}
