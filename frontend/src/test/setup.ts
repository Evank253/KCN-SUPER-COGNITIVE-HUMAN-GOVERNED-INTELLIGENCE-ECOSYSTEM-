/** Vitest test setup — imports jest-dom matchers. */
import '@testing-library/jest-dom'

// jsdom has no WebGL/2D canvas implementation. Components like HyperspacePortal
// call canvas.getContext('webgl') defensively and no-op when it returns null,
// but jsdom logs a noisy "not implemented" error to stderr on every call.
// Stub it so tests stay quiet without needing the native `canvas` package.
if (typeof HTMLCanvasElement !== 'undefined') {
  HTMLCanvasElement.prototype.getContext = (() => null) as typeof HTMLCanvasElement.prototype.getContext
}
