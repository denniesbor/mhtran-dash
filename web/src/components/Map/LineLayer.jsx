// Role: pure SVG render of transmission line features
// Author: Dennies Bor

import * as d3 from "d3";
import { useMapContext } from "./USMap.jsx";
import { NULL_COLOR } from "../../lib/colorScale.js";

const widthScale = d3.scaleSqrt().domain([69, 765]).range([0.5, 2.5]);

export default function LineLayer({ features, hazard, colorScale, onHover, onLeave }) {
  const { projection, transform } = useMapContext();
  if (!features?.length) return null;

  const key = `ead_${hazard}`;
  const pathGen = d3.geoPath().projection(projection);
  const strokeWidth = (kv) => widthScale(kv ?? 69) / transform.k;

  return (
    <g>
      {features.map((f) => {
        const d = pathGen(f.geometry);
        if (!d) return null;

        const ead = f.properties[key];
        const stroke = ead != null ? colorScale(ead) : NULL_COLOR;
        const kv = f.properties.voltage_kv;

        return (
          <path
            key={f.properties.name}
            d={d}
            fill="none"
            stroke={stroke}
            strokeWidth={strokeWidth(kv)}
            strokeOpacity={0.6}
            strokeLinecap="round"
            strokeLinejoin="round"
            style={{ cursor: "pointer" }}
            onMouseEnter={(e) => onHover?.({ type: "line", feature: f, hazard }, e)}
            onMouseLeave={onLeave}
          />
        );
      })}
    </g>
  );
}
