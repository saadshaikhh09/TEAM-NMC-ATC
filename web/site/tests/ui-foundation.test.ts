import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import test from 'node:test'
import { scrollProgress } from '../src/lib/progress.ts'

test('scroll progress is exactly bounded', () => {
  assert.equal(scrollProgress(0, 3000, 1000), 0)
  assert.equal(scrollProgress(2000, 3000, 1000), 1)
  assert.equal(scrollProgress(2500, 3000, 1000), 1)
  assert.equal(scrollProgress(-10, 3000, 1000), 0)
  assert.equal(scrollProgress(0, 800, 1000), 0)
})

test('stacked cards have mobile, short-height and reduced-motion fallbacks', () => {
  const css = readFileSync(new URL('../src/site.css', import.meta.url), 'utf8')
  assert.match(css, /@media \(max-width: 720px\)[\s\S]*\.stage-card[^}]*position: relative/)
  assert.match(css, /@media \(max-height: 720px\)[\s\S]*\.stage-card[^}]*position: relative/)
  assert.match(css, /@media \(prefers-reduced-motion: reduce\)[\s\S]*\.stage-card[^}]*position: relative/)
})

test('ordinary pages do not use a blanket horizontal overflow mask', () => {
  const css = readFileSync(new URL('../src/site.css', import.meta.url), 'utf8')
  assert.doesNotMatch(css, /html\s*,?\s*body[^}]*overflow-x\s*:\s*(hidden|clip)/)
})
