// Role: cursor-following tooltip card for map feature hover
// Author: Dennies Bor

import { HAZARD_LABELS } from "../lib/constants.js";

const usd = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

function Row({ label, value }) {
  return (
    <div className="flex justify-between gap-4">
      <span className="text-ink-muted">{label}</span>
      <span className="font-medium text-right">{value}</span>
    </div>
  );
}

function SubContent({ feature, hazard }) {
  const p = feature.properties;
  const ead = p[`ead_${hazard}`];
  return (
    <>
      <div className="font-semibold text-ink mb-1 leading-snug">
        {p.ss_name ?? p.ss_id}
      </div>
      {p.ss_operator && (
        <Row label="Operator" value={p.ss_operator} />
      )}
      <Row label="Voltage" value={`${p.max_voltage_kv ?? "—"} kV`} />
      <Row label="Class" value={p.asset_class ?? "—"} />
      <div className="border-t border-line mt-1.5 pt-1.5">
        <Row
          label={`EAD — ${HAZARD_LABELS[hazard] ?? hazard}`}
          value={ead != null ? usd.format(ead) + "/yr" : "outside scope"}
        />
      </div>
    </>
  );
}

function LineContent({ feature, hazard }) {
  const p = feature.properties;
  const ead = p[`ead_${hazard}`];
  return (
    <>
      <div className="font-semibold text-ink mb-1 leading-snug truncate max-w-[200px]">
        {p.name}
      </div>
      <Row label="Voltage" value={`${p.voltage_kv ?? "—"} kV`} />
      <Row label="Length" value={p.length_km != null ? `${p.length_km.toFixed(0)} km` : "—"} />
      {hazard && (
        <div className="border-t border-line mt-1.5 pt-1.5">
          <Row
            label={`EAD — ${HAZARD_LABELS[hazard] ?? hazard}`}
            value={ead != null ? usd.format(ead) + "/yr" : "outside scope"}
          />
        </div>
      )}
    </>
  );
}

/** Rendered at cursor position. Pass null tooltip to hide. */
export default function Tooltip({ tooltip }) {
  if (!tooltip) return null;

  const { x, y, type, feature, hazard } = tooltip;

  // Keep tooltip on screen — flip left if near right edge
  const style = {
    position: "fixed",
    top: y - 8,
    left: x + 14,
    transform: "translateY(-50%)",
    pointerEvents: "none",
    zIndex: 50,
    maxWidth: 240,
  };

  return (
    <div
      style={style}
      className="bg-white border border-line rounded-lg shadow-lg px-3 py-2 text-xs text-ink"
    >
      {type === "sub" ? (
        <SubContent feature={feature} hazard={hazard} />
      ) : (
        <LineContent feature={feature} hazard={hazard} />
      )}
    </div>
  );
}
