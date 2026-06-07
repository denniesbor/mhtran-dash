// Role: encapsulates d3.zoom imperative wiring onto an SVG ref
// Author: Dennies Bor

import { useEffect, useRef, useState } from "react";
import * as d3 from "d3";

/**
 * Attach d3.zoom to svgRef. Returns the current d3 ZoomTransform.
 * Callers apply it to a <g> via transform.toString().
 */
export function useZoom(svgRef) {
  const [transform, setTransform] = useState(() => d3.zoomIdentity);
  // keep a stable ref so the cleanup closure doesn't capture a stale element
  const svgElRef = useRef(null);

  useEffect(() => {
    const el = svgRef.current;
    if (!el) return;
    svgElRef.current = el;

    const zoom = d3
      .zoom()
      .scaleExtent([1, 8])
      .translateExtent([
        [0, 0],
        [960, 600],
      ])
      .on("zoom", (event) => setTransform(event.transform));

    d3.select(el).call(zoom);

    return () => {
      d3.select(el).on(".zoom", null);
    };
  }, [svgRef]);

  return transform;
}
