/** User preferences — Jarvis + sound. Persisted in localStorage. */

const SOUND_KEY = "kcn_sound_enabled";
const JARVIS_KEY = "kcn_jarvis_enabled";

export function isSoundEnabled() {
  if (typeof window === "undefined") return true;
  const v = localStorage.getItem(SOUND_KEY);
  return v === null ? true : v === "1";
}

export function setSoundEnabled(on) {
  if (typeof window === "undefined") return;
  localStorage.setItem(SOUND_KEY, on ? "1" : "0");
  window.dispatchEvent(new CustomEvent("kcn-prefs", { detail: { sound: on } }));
}

export function isJarvisEnabled() {
  if (typeof window === "undefined") return true;
  const v = localStorage.getItem(JARVIS_KEY);
  return v === null ? true : v === "1";
}

export function setJarvisEnabled(on) {
  if (typeof window === "undefined") return;
  localStorage.setItem(JARVIS_KEY, on ? "1" : "0");
  window.dispatchEvent(new CustomEvent("kcn-prefs", { detail: { jarvis: on } }));
}

export function getPrefs() {
  return {
    sound: isSoundEnabled(),
    jarvis: isJarvisEnabled(),
  };
}
