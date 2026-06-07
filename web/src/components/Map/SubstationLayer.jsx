// Role: pure SVG render of substation point features
// Author: Dennies Bor

import * as d3 from "d3";
import { useMapContext } from "./USMap.jsx";
import { NULL_COLOR } from "../../lib/colorScale.js";

const radiusScale = d3.scaleSqrt().domain([69, 765]).range([2, 8]);

export default function SubstationLayer({ features, hazard, colorScale, onHover, onLeave }) {
  const { projection, transform } = useMapContext();
  if (!features?.length) return null;

  const key = `ead_${hazard}`;
  const r = (kv) => radiusScale(kv ?? 69) / transform.k;

  return (
    <g>
      {features.map((f) => {
        const [lon, lat] = f.geometry.coordinates;
        const projected = projection([lon, lat]);
        if (!projected) return null;

        const [x, y] = projected;
        const ead = f.properties[key];
        const fill = ead != null ? colorScale(ead) : NULL_COLOR;
        const kv = f.properties.max_voltage_kv;

        return (
          <circle
            key={f.properties.ss_id}
            cx={x}
            cy={y}
            r={r(kv)}
            fill={fill}
            fillOpacity={0.85}
            stroke="#fff"
            strokeWidth={0.3 / transform.k}
            style={{ cursor: "pointer" }}
            onMouseEnter={(e) => onHover?.({ type: "sub", feature: f, hazard }, e)}
            onMouseLeave={onLeave}
          />
        );
      })}
    </g>
  );
}
