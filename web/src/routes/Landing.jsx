// Role: welcome / landing page — full-screen dark hero, paper metadata, key stats, CTAs
// Author: Dennies Bor

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

const STATS = [
  { value: "$137 M/day", label: "TC Wind — direct damage",  sub: "Largest individual hazard" },
  { value: "$4.93 B/day", label: "Tornado — output loss",   sub: "Largest downstream impact" },
  { value: "$2.07 B/day", label: "Geomagnetic 250-yr",      sub: "Space weather on par w/ terrestrial" },
  { value: "$85 B/day",   label: "Compound FZG stress test", sub: "Upper-bound disruption" },
  { value: "13,000+",     label: "Line segments",            sub: "US HV transmission network" },
  { value: "10,000+",     label: "Substations analyzed",     sub: "All voltage classes" },
];

export default function Landing() {
  const [visible, setVisible] = useState(false);
  useEffect(() => {
    const t = setTimeout(() => setVisible(true), 80);
    return () => clearTimeout(t);
  }, []);

  return (
    <div className="fixed inset-0 overflow-auto" style={{ background: "#030712" }}>

      {/* subtle grid */}
      <div className="absolute inset-0 pointer-events-none" style={{
        backgroundImage:
          "linear-gradient(rgba(37,99,235,0.05) 1px, transparent 1px)," +
          "linear-gradient(90deg, rgba(37,99,235,0.05) 1px, transparent 1px)",
        backgroundSize: "64px 64px",
      }} />

      {/* centre radial glow */}
      <div className="absolute inset-0 pointer-events-none" style={{
        background: "radial-gradient(ellipse 90% 60% at 50% 38%, rgba(37,99,235,0.10) 0%, transparent 68%)",
      }} />

      <div
        className="relative z-10 min-h-full flex flex-col items-center justify-center px-6 py-16"
        style={{
          opacity: visible ? 1 : 0,
          transform: visible ? "translateY(0)" : "translateY(12px)",
          transition: "opacity 0.65s ease, transform 0.65s cubic-bezier(0.34,1.2,0.64,1)",
        }}
      >
        {/* eyebrow */}
        <div className="mb-4 flex items-center gap-2">
          <span
            className="text-[10px] font-mono tracking-widest uppercase"
            style={{ color: "rgba(96,165,250,0.7)" }}
          >
            arXiv · 2605.23053
          </span>
          <span
            className="text-[10px] font-mono tracking-widest"
            style={{ color: "rgba(100,116,139,0.6)" }}
          >
            · Preprint 2026
          </span>
        </div>

        {/* title */}
        <h1
          className="text-center font-bold leading-tight text-white mb-3 max-w-3xl"
          style={{ fontSize: "clamp(1.45rem, 4vw, 2.6rem)" }}
        >
          Multi-Hazard Risk Assessment
          <br />
          <span style={{
            background: "linear-gradient(130deg, #60a5fa 0%, #a78bfa 55%, #f472b6 100%)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
          }}>
            of the US High-Voltage Transmission Network
          </span>
        </h1>

        {/* author */}
        <p className="text-sm mb-1" style={{ color: "#94a3b8" }}>
          Dennies Bor · George Mason University
        </p>
        <p className="text-xs mb-6" style={{ color: "rgba(100,116,139,0.75)" }}>
          PhD Candidate, Earth Systems and Geoinformation Sciences
        </p>

        {/* tagline */}
        <p
          className="text-sm text-center max-w-lg mb-10 leading-relaxed"
          style={{ color: "rgba(148,163,184,0.85)" }}
        >
          An integrated framework linking hazard characterisation, fragility
          modelling, and macroeconomic impact propagation across ten natural
          hazards — establishing a consistent baseline for prioritising
          grid resilience investments.
        </p>

        {/* CTAs */}
        <div className="flex flex-wrap gap-3 justify-center mb-14">
          <Link
            to="/map"
            className="px-5 py-2.5 rounded-xl text-sm font-semibold text-white transition-all"
            style={{
              background: "linear-gradient(135deg, #2563eb, #1d4ed8)",
              boxShadow: "0 8px 24px rgba(37,99,235,0.30)",
            }}
            onMouseEnter={e => { e.currentTarget.style.boxShadow = "0 12px 32px rgba(37,99,235,0.45)"; e.currentTarget.style.transform = "translateY(-2px)"; }}
            onMouseLeave={e => { e.currentTarget.style.boxShadow = "0 8px 24px rgba(37,99,235,0.30)"; e.currentTarget.style.transform = ""; }}
          >
            Explore Map
          </Link>

          <Link
            to="/compare"
            className="px-5 py-2.5 rounded-xl text-sm font-semibold transition-colors"
            style={{
              color: "#cbd5e1",
              border: "1px solid rgba(100,116,139,0.45)",
            }}
            onMouseEnter={e => e.currentTarget.style.borderColor = "rgba(100,116,139,0.8)"}
            onMouseLeave={e => e.currentTarget.style.borderColor = "rgba(100,116,139,0.45)"}
          >
            Paper Summary
          </Link>

          <a
            href="https://arxiv.org/abs/2605.23053"
            target="_blank" rel="noreferrer"
            className="px-5 py-2.5 rounded-xl text-sm font-medium transition-colors"
            style={{
              color: "#60a5fa",
              border: "1px solid rgba(96,165,250,0.25)",
            }}
            onMouseEnter={e => e.currentTarget.style.borderColor = "rgba(96,165,250,0.55)"}
            onMouseLeave={e => e.currentTarget.style.borderColor = "rgba(96,165,250,0.25)"}
          >
            arXiv ↗
          </a>
        </div>

        {/* stats grid */}
        <div
          className="grid grid-cols-2 sm:grid-cols-3 max-w-2xl w-full rounded-2xl overflow-hidden"
          style={{
            border: "1px solid rgba(51,65,85,0.5)",
            background: "rgba(15,23,42,0.6)",
            gap: "1px",
            boxShadow: "0 0 0 1px rgba(51,65,85,0.35) inset",
          }}
        >
          {STATS.map(({ value, label, sub }, i) => (
            <div
              key={label}
              className="px-5 py-4"
              style={{
                background: i % 2 === 0 ? "rgba(10,15,30,0.7)" : "rgba(8,12,24,0.7)",
                borderRight: (i % 3 !== 2) ? "1px solid rgba(51,65,85,0.35)" : "none",
                borderBottom: i < 3 ? "1px solid rgba(51,65,85,0.35)" : "none",
              }}
            >
              <div className="text-lg font-bold leading-tight" style={{ color: "#93c5fd" }}>
                {value}
              </div>
              <div className="text-xs font-medium mt-0.5" style={{ color: "rgba(226,232,240,0.85)" }}>
                {label}
              </div>
              <div className="text-[10px] mt-0.5" style={{ color: "rgba(100,116,139,0.7)" }}>
                {sub}
              </div>
            </div>
          ))}
        </div>

        {/* footer note */}
        <p className="mt-10 text-[11px] text-center" style={{ color: "rgba(100,116,139,0.55)" }}>
          Dashboard · React + D3 · Analysis code at{" "}
          <a
            href="https://github.com/denniesbor/mhtran"
            target="_blank" rel="noreferrer"
            className="hover:underline"
            style={{ color: "rgba(96,165,250,0.6)" }}
          >
            github.com/denniesbor/mhtran
          </a>
        </p>
      </div>
    </div>
  );
}
