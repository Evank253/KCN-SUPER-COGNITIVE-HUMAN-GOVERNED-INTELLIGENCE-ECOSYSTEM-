import { isSoundEnabled } from "./prefs";

let _ctx = null;

function ctx() {
  if (typeof window === "undefined") return null;
  if (!isSoundEnabled()) return null;
  if (!_ctx) _ctx = new (window.AudioContext || window.webkitAudioContext)();
  if (_ctx.state === "suspended") _ctx.resume();
  return _ctx;
}

export function playTone({ freq = 440, duration = 0.08, type = "sine", gain = 0.04, slide = 0 } = {}) {
  if (!isSoundEnabled()) return;
  const c = ctx();
  if (!c) return;
  try {
    const osc = c.createOscillator();
    const g = c.createGain();
    osc.type = type;
    osc.frequency.setValueAtTime(freq, c.currentTime);
    if (slide) osc.frequency.linearRampToValueAtTime(freq + slide, c.currentTime + duration);
    g.gain.setValueAtTime(gain, c.currentTime);
    g.gain.exponentialRampToValueAtTime(0.001, c.currentTime + duration);
    osc.connect(g);
    g.connect(c.destination);
    osc.start();
    osc.stop(c.currentTime + duration + 0.02);
  } catch (_) {}
}

export function soundHover() {
  playTone({ freq: 920, duration: 0.04, type: "sine", gain: 0.018 });
}

export function soundClick() {
  playTone({ freq: 540, duration: 0.055, type: "triangle", gain: 0.045, slide: 160 });
}

export function soundWhoosh() {
  playTone({ freq: 180, duration: 0.28, type: "sawtooth", gain: 0.028, slide: 420 });
}

export function soundSuccess() {
  playTone({ freq: 523, duration: 0.07, type: "sine", gain: 0.035 });
  setTimeout(() => playTone({ freq: 659, duration: 0.09, type: "sine", gain: 0.035 }), 70);
  setTimeout(() => playTone({ freq: 784, duration: 0.1, type: "sine", gain: 0.03 }), 150);
}

export function soundBoot() {
  if (!isSoundEnabled()) return;
  playTone({ freq: 90, duration: 0.35, type: "sine", gain: 0.045, slide: 220 });
  setTimeout(() => playTone({ freq: 330, duration: 0.12, type: "triangle", gain: 0.03 }), 180);
  setTimeout(() => playTone({ freq: 520, duration: 0.15, type: "sine", gain: 0.028 }), 320);
}

export function soundTransmit() {
  playTone({ freq: 400, duration: 0.05, type: "square", gain: 0.02 });
  setTimeout(() => playTone({ freq: 600, duration: 0.08, type: "sine", gain: 0.025, slide: 100 }), 40);
}

export function soundAlert() {
  playTone({ freq: 280, duration: 0.12, type: "sawtooth", gain: 0.03 });
  setTimeout(() => playTone({ freq: 220, duration: 0.15, type: "sawtooth", gain: 0.025 }), 100);
}
