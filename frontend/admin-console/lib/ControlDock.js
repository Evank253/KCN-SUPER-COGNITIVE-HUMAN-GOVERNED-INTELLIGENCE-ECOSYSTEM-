import { useEffect, useState } from "react";
import {
  getPrefs,
  setSoundEnabled,
  setJarvisEnabled,
} from "./prefs";
import { soundClick, soundBoot } from "./sound";

/** Floating cinematic controls — Jarvis + Sound toggles. */
export default function ControlDock() {
  const [sound, setSound] = useState(true);
  const [jarvis, setJarvis] = useState(true);
  const [open, setOpen] = useState(true);

  useEffect(() => {
    const p = getPrefs();
    setSound(p.sound);
    setJarvis(p.jarvis);
    const onPrefs = (e) => {
      if (e.detail?.sound !== undefined) setSound(e.detail.sound);
      if (e.detail?.jarvis !== undefined) setJarvis(e.detail.jarvis);
    };
    window.addEventListener("kcn-prefs", onPrefs);
    return () => window.removeEventListener("kcn-prefs", onPrefs);
  }, []);

  function toggleSound() {
    const next = !sound;
    setSoundEnabled(next);
    setSound(next);
    if (next) {
      soundClick();
      setTimeout(() => soundBoot(), 50);
    }
  }

  function toggleJarvis() {
    const next = !jarvis;
    setJarvisEnabled(next);
    setJarvis(next);
    if (sound) soundClick();
  }

  const dock = { position: "fixed", right: 18, bottom: 18, zIndex: 10000, fontFamily: "Inter, system-ui, sans-serif" };
  const panel = {
    background: "linear-gradient(160deg, rgba(12,20,40,0.94), rgba(6,10,22,0.96))",
    border: "1px solid rgba(96,165,250,0.4)",
    borderRadius: 16,
    padding: open ? "14px 16px" : "10px 12px",
    backdropFilter: "blur(18px)",
    boxShadow: "0 16px 48px rgba(0,0,0,0.5), 0 0 32px rgba(59,130,246,0.15)",
    minWidth: open ? 200 : 0,
  };
  const row = { display: "flex", alignItems: "center", justifyContent: "space-between", gap: 14, marginTop: 10 };
  const label = { fontSize: 11, letterSpacing: "0.12em", textTransform: "uppercase", color: "#94a3b8", fontWeight: 600 };
  const toggle = (on) => ({
    width: 44, height: 24, borderRadius: 999, border: "none", cursor: "pointer", position: "relative",
    background: on ? "linear-gradient(90deg, #059669, #0ea5e9)" : "rgba(51,65,85,0.9)",
    boxShadow: on ? "0 0 16px rgba(14,165,233,0.45)" : "none",
  });
  const knob = (on) => ({
    position: "absolute", top: 3, left: on ? 22 : 3, width: 18, height: 18, borderRadius: "50%",
    background: "#fff", transition: "left 0.22s cubic-bezier(0.22,1,0.36,1)",
  });

  return (
    <div style={dock}>
      <div style={panel}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12, cursor: "pointer" }} onClick={() => setOpen(!open)}>
          <div style={{ fontSize: 10, letterSpacing: "0.18em", textTransform: "uppercase", color: "#7dd3fc", fontWeight: 700 }}>
            <span style={{ display: "inline-block", width: 7, height: 7, borderRadius: "50%", background: jarvis ? "#34d399" : "#64748b", marginRight: 8, boxShadow: jarvis ? "0 0 10px #34d399" : "none" }} />
            Control deck
          </div>
          <span style={{ color: "#64748b", fontSize: 12 }}>{open ? "▾" : "▸"}</span>
        </div>
        {open && (
          <>
            <div style={row}>
              <span style={label}>Sound FX</span>
              <button type="button" aria-label="Toggle sound" style={toggle(sound)} onClick={(e) => { e.stopPropagation(); toggleSound(); }}>
                <span style={knob(sound)} />
              </button>
            </div>
            <div style={row}>
              <span style={label}>Jarvis</span>
              <button type="button" aria-label="Toggle Jarvis" style={toggle(jarvis)} onClick={(e) => { e.stopPropagation(); toggleJarvis(); }}>
                <span style={knob(jarvis)} />
              </button>
            </div>
            <div style={{ marginTop: 12, fontSize: 10, color: "#64748b", lineHeight: 1.4 }}>
              {jarvis ? "Jarvis mission layer active in chat" : "Jarvis offline — chat only"}
              {" · "}
              {sound ? "Audio on" : "Muted"}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
