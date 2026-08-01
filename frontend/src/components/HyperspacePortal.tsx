/**
 * HyperspacePortal — pure WebGL (no extra deps)
 * Startup starfield → warp burst, then interactive portal tunnel on demand.
 */

import { useEffect, useRef, useCallback } from 'react'

interface HyperspacePortalProps {
  /** 0 = idle ambient, 1 = full warp tunnel */
  intensity?: number
  /** Trigger a short warp burst (e.g. on navigation) */
  warpTrigger?: number
  className?: string
  style?: React.CSSProperties
}

const VERT = `
attribute vec2 a_pos;
void main() {
  gl_Position = vec4(a_pos, 0.0, 1.0);
}
`

const FRAG = `
precision highp float;
uniform float u_time;
uniform vec2 u_res;
uniform float u_intensity;
uniform float u_warp;

// Hash for pseudo-random stars
float hash(vec2 p) {
  return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

void main() {
  vec2 uv = (gl_FragCoord.xy - 0.5 * u_res) / min(u_res.x, u_res.y);
  float r = length(uv);
  float a = atan(uv.y, uv.x);

  // Deep space base
  vec3 col = vec3(0.01, 0.02, 0.06);

  // Radial tunnel rings (hyperspace)
  float tunnel = 0.0;
  float speed = 1.2 + u_warp * 8.0 + u_intensity * 3.0;
  for (int i = 0; i < 8; i++) {
    float fi = float(i);
    float z = fract(fi * 0.125 + u_time * speed * 0.15);
    float rad = (0.05 + z * 1.4) / (r + 0.08);
    float ring = smoothstep(0.08, 0.0, abs(rad - 1.0 / (r + 0.15) * z));
    float glow = exp(-r * (2.0 + z * 4.0)) * (1.0 - z);
    tunnel += ring * glow * (0.4 + 0.6 * u_intensity + u_warp);
  }

  // Streak lines (warp)
  float streaks = 0.0;
  for (int i = 0; i < 40; i++) {
    float fi = float(i);
    float h = hash(vec2(fi, fi * 1.7));
    float ang = h * 6.2832;
    float d = abs(sin(a - ang) * r);
    float len = fract(h + u_time * (2.0 + u_warp * 12.0));
    float star = smoothstep(0.015 + u_warp * 0.02, 0.0, d)
               * smoothstep(0.0, 0.35, len)
               * (1.0 - smoothstep(0.35, 1.0, len))
               * (0.3 + u_intensity + u_warp * 1.5);
    streaks += star * (0.5 + 0.5 * h);
  }

  // Center portal core
  float core = exp(-r * r * (8.0 - u_warp * 5.0));
  vec3 coreCol = mix(
    vec3(0.15, 0.35, 1.0),
    vec3(0.6, 0.2, 1.0),
    0.5 + 0.5 * sin(u_time * 2.0)
  );

  // Chromatic rim
  float rim = smoothstep(0.55, 0.25, r) * (0.15 + u_intensity * 0.25);

  col += tunnel * vec3(0.2, 0.5, 1.0);
  col += streaks * vec3(0.7, 0.85, 1.0);
  col += core * coreCol * (0.8 + u_warp * 1.5);
  col += rim * vec3(0.4, 0.2, 0.9);

  // Vignette
  col *= 1.0 - smoothstep(0.4, 1.35, r);

  // Subtle scanline
  col *= 0.96 + 0.04 * sin(gl_FragCoord.y * 1.5);

  gl_FragColor = vec4(col, 1.0);
}
`

function createShader(gl: WebGLRenderingContext, type: number, src: string) {
  const s = gl.createShader(type)
  if (!s) return null
  gl.shaderSource(s, src)
  gl.compileShader(s)
  if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) {
    console.warn(gl.getShaderInfoLog(s))
    gl.deleteShader(s)
    return null
  }
  return s
}

export default function HyperspacePortal({
  intensity = 0.35,
  warpTrigger = 0,
  className,
  style,
}: HyperspacePortalProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const warpRef = useRef(0)
  const intensityRef = useRef(intensity)
  const rafRef = useRef(0)

  intensityRef.current = intensity

  // Burst warp when trigger increments
  useEffect(() => {
    if (warpTrigger > 0) {
      warpRef.current = 1
    }
  }, [warpTrigger])

  const setup = useCallback(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const gl = canvas.getContext('webgl', {
      alpha: false,
      antialias: false,
      powerPreference: 'high-performance',
    })
    if (!gl) return

    const vs = createShader(gl, gl.VERTEX_SHADER, VERT)
    const fs = createShader(gl, gl.FRAGMENT_SHADER, FRAG)
    if (!vs || !fs) return

    const prog = gl.createProgram()
    if (!prog) return
    gl.attachShader(prog, vs)
    gl.attachShader(prog, fs)
    gl.linkProgram(prog)
    if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) {
      console.warn(gl.getProgramInfoLog(prog))
      return
    }
    gl.useProgram(prog)

    const buf = gl.createBuffer()
    gl.bindBuffer(gl.ARRAY_BUFFER, buf)
    gl.bufferData(
      gl.ARRAY_BUFFER,
      new Float32Array([-1, -1, 1, -1, -1, 1, -1, 1, 1, -1, 1, 1]),
      gl.STATIC_DRAW,
    )
    const aPos = gl.getAttribLocation(prog, 'a_pos')
    gl.enableVertexAttribArray(aPos)
    gl.vertexAttribPointer(aPos, 2, gl.FLOAT, false, 0, 0)

    const uTime = gl.getUniformLocation(prog, 'u_time')
    const uRes = gl.getUniformLocation(prog, 'u_res')
    const uIntensity = gl.getUniformLocation(prog, 'u_intensity')
    const uWarp = gl.getUniformLocation(prog, 'u_warp')

    const resize = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, 2)
      const w = canvas.clientWidth
      const h = canvas.clientHeight
      canvas.width = Math.floor(w * dpr)
      canvas.height = Math.floor(h * dpr)
      gl.viewport(0, 0, canvas.width, canvas.height)
    }
    resize()
    window.addEventListener('resize', resize)

    const t0 = performance.now()
    const frame = (now: number) => {
      const t = (now - t0) / 1000

      // Decay warp burst
      if (warpRef.current > 0) {
        warpRef.current = Math.max(0, warpRef.current - 0.012)
      }

      // Startup ramp: first ~2.5s intensity climbs then settles
      const boot = Math.min(1, t / 2.2)
      const bootBoost = Math.sin(boot * Math.PI) * 0.85
      const i = Math.min(1, intensityRef.current + bootBoost * (t < 2.8 ? 1 : 0))

      gl.uniform1f(uTime, t)
      gl.uniform2f(uRes, canvas.width, canvas.height)
      gl.uniform1f(uIntensity, i)
      gl.uniform1f(uWarp, warpRef.current)
      gl.drawArrays(gl.TRIANGLES, 0, 6)

      rafRef.current = requestAnimationFrame(frame)
    }
    rafRef.current = requestAnimationFrame(frame)

    return () => {
      window.removeEventListener('resize', resize)
      cancelAnimationFrame(rafRef.current)
    }
  }, [])

  useEffect(() => {
    const cleanup = setup()
    return () => {
      cleanup?.()
    }
  }, [setup])

  return (
    <canvas
      ref={canvasRef}
      className={className}
      style={{
        position: 'absolute',
        inset: 0,
        width: '100%',
        height: '100%',
        display: 'block',
        pointerEvents: 'none',
        ...style,
      }}
      aria-hidden
    />
  )
}
