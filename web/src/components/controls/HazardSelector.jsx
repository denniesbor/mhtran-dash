// Role: floating map card — shows active hazard, expands to pick another
// Author: Dennies Bor

import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import { HAZARDS, HAZARD_LABELS, LINE_HAZARDS, DEFAULT_HAZARD } from "../../lib/constants.js";

export default function HazardSelector({ hasRaster = false, showRaster = true, onToggleRaster, geomag = null, onGeomagChange }) {
  const [open, setOpen] = useState(false);
  const [searchParams, setSearchParams] = useSearchParams();
  const active = searchParams.get("hazard") ?? DEFAULT_HAZARD;

  function select(h) {
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev);
      next.set("hazard", h);
      return next;
    });
    setOpen(false);
  }

  return (
    <div className="absolute top-3 left-3 z-10 w-44 select-none">
      {/* trigger */}
      <button
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center justify-between gap-2 px-3 py-2 rounded-lg bg-white border border-line shadow-md text-sm font-medium text-ink hover:border-ink-muted transition-colors"
      >
        <span className="flex flex-col items-start leading-tight">
          <span className="text-[10px] font-normal text-ink-muted uppercase tracking-wide">
            Hazard
          </span>
          <span>{HAZARD_LABELS[active]}</span>
        </span>
        <svg
          className={`w-4 h-4 text-ink-muted transition-transform ${open ? "rotate-180" : ""}`}
          viewBox="0 0 20 20"
          fill="currentColor"
        >
          <path
            fillRule="evenodd"
            d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z"
            clipRule="evenodd"
          />
        </svg>
      </button>

      {/* raster toggle — only when current hazard has a prebuilt PNG */}
      {hasRaster && (
        <button
          onClick={onToggleRaster}
          className={[
            "mt-1 w-full flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs font-medium transition-colors shadow-sm",
            showRaster
              ? "bg-accent border-accent text-white"
              : "bg-white border-line text-ink-muted hover:border-ink-muted",
          ].join(" ")}
        >
          <svg className="w-3.5 h-3.5 shrink-0" viewBox="0 0 20 20" fill="currentColor">
            <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
            <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd" />
          </svg>
          Intensity layer
        </button>
      )}

      {/* geomag-specific: field type and return period toggles */}
      {geomag && showRaster && (
        <div className="mt-1 rounded-lg bg-white border border-line shadow-sm overflow-hidden text-xs">
          <div className="px-2 pt-1.5 pb-0.5 text-[10px] font-normal text-ink-muted uppercase tracking-wide">Field</div>
          <div className="flex gap-1 px-2 pb-1.5">
            {["E", "B"].map((f) => (
              <button
                key={f}
                onClick={() => onGeomagChange(prev => ({ ...prev, field: f }))}
                className={[
                  "flex-1 py-0.5 rounded border text-xs font-medium transition-colors",
                  geomag.field === f
                    ? "bg-accent border-accent text-white"
                    : "bg-white border-line text-ink-muted hover:border-ink-muted",
                ].join(" ")}
              >
                {f === "E" ? "E-field" : "B-field"}
              </button>
            ))}
          </div>
          <div className="px-2 pt-0.5 pb-0.5 text-[10px] font-normal text-ink-muted uppercase tracking-wide">Return period</div>
          <div className="flex gap-1 px-2 pb-1.5">
            {[100, 250].map((rp) => (
              <button
                key={rp}
                onClick={() => onGeomagChange(prev => ({ ...prev, rp }))}
                className={[
                  "flex-1 py-0.5 rounded border text-xs font-medium transition-colors",
                  geomag.rp === rp
                    ? "bg-accent border-accent text-white"
                    : "bg-white border-line text-ink-muted hover:border-ink-muted",
                ].join(" ")}
              >
                {rp}-yr
              </button>
            ))}
          </div>
        </div>
      )}

      {/* dropdown list */}
      {open && (
        <ul className="mt-1 rounded-lg bg-white border border-line shadow-lg overflow-hidden text-sm">
          {HAZARDS.map((h) => {
            const isActive = h === active;
            const subsOnly = !LINE_HAZARDS.has(h);
            return (
              <li key={h}>
                <button
                  onClick={() => select(h)}
                  className={[
                    "w-full text-left px-3 py-1.5 flex items-center justify-between transition-colors",
                    isActive
                      ? "bg-accent text-white"
                      : "text-ink hover:bg-surface-inset",
                  ].join(" ")}
                >
                  {HAZARD_LABELS[h]}
                  {subsOnly && (
                    <span
                      className={`text-[10px] ${isActive ? "text-blue-200" : "text-ink-muted"}`}
                    >
                      subs only
                    </span>
                  )}
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
