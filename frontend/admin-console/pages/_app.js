import "../styles/global.css";
import WebGLScene from "../lib/WebGLScene";
import ControlDock from "../lib/ControlDock";
import { useEffect } from "react";
import { soundBoot } from "../lib/sound";
import { isSoundEnabled } from "../lib/prefs";

export default function App({ Component, pageProps }) {
  useEffect(() => {
    const unlock = () => {
      if (isSoundEnabled()) soundBoot();
      window.removeEventListener("pointerdown", unlock);
    };
    window.addEventListener("pointerdown", unlock, { once: true });
  }, []);

  return (
    <>
      <WebGLScene variant="admin" />
      <div className="kcn-shell">
        <Component {...pageProps} />
      </div>
      <ControlDock />
    </>
  );
}
