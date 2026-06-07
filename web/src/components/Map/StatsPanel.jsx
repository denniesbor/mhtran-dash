// Role: floating map overlay showing aggregate EAD stats for the active hazard
// Author: Dennies Bor

import { useMemo } from "react";
import { HAZARD_LABELS } from "../../lib/constants.js";

const usdCompact = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  notation: "compact",
  compactDisplay: "short",
  maximumFractionDigits: 1,
});

const numFmt = new Intl.NumberFormat("en-US");

function Stat({ label, value, sub }) {
  return (
    <div className="flex flex-col">
      <span className="text-[10px] uppercase tracking-wide text-ink-muted">{label}</span>
      <span className="text-lg font-bold text-ink leading-tight">{value}</span>
      {sub && <span className="text-[10px] text-ink-muted">{sub}</span>}
    </div>
  );
}

export default function StatsPanel({ subFeatures, lineFeatures, hazard, geomag }) {
  const stats = useMemo(() => {
    // For geomag, use the scenario-specific EAD column (100yr or 250yr event damage).
    const eadKey = hazard === "geomag" && geomag
      ? `ead_geomag_${geomag.rp}`
      : `ead_${hazard}`;
    const costKey = "replacement_cost_usd";

    let totalSubEAD = 0;
    let atRiskSubs = 0;
    let totalSubCost = 0;

    for (const f of subFeatures) {
      const p = f.properties;
      const ead = p[eadKey];
      if (ead != null && ead > 0) {
        totalSubEAD += ead;
        atRiskSubs++;
        totalSubCost += p[costKey] ?? 0;
      }
    }

    let totalLineEAD = 0;
    let atRiskLines = 0;

    for (const f of lineFeatures) {
      const ead = f.properties[eadKey];
      if (ead != null && ead > 0) {
        totalLineEAD += ead;
        atRiskLines++;
      }
    }

    return { totalSubEAD, atRiskSubs, totalSubCost, totalLineEAD, atRiskLines };
  }, [subFeatures, lineFeatures, hazard, geomag]);

  if (!subFeatures.length && !lineFeatures.length) return null;

  const hazardLabel = HAZARD_LABELS[hazard] ?? hazard;

  return (
    <div className="absolute top-3 right-3 z-10 bg-white border border-line rounded-lg shadow-md px-4 py-3 w-56">
      <div className="text-[10px] font-semibold uppercase tracking-widest text-ink-muted mb-2">
        {hazardLabel} —{" "}
        {hazard === "geomag" && geomag
          ? `${geomag.rp}-yr Event Damage`
          : "Annual Expected Damage"}
      </div>

      <div className="grid grid-cols-2 gap-x-4 gap-y-2.5">
        <Stat
          label="Substations EAD"
          value={usdCompact.format(stats.totalSubEAD)}
          sub={`${numFmt.format(stats.atRiskSubs)} in scope`}
        />
        <Stat
          label="Lines EAD"
          value={usdCompact.format(stats.totalLineEAD)}
          sub={`${numFmt.format(stats.atRiskLines)} in scope`}
        />
        <Stat
          label="Total EAD"
          value={usdCompact.format(stats.totalSubEAD + stats.totalLineEAD)}
          sub="subs + lines"
        />
        <Stat
          label="Exposed Asset Value"
          value={usdCompact.format(stats.totalSubCost)}
          sub="replacement cost"
        />
      </div>
    </div>
  );
}
