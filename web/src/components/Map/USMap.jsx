// Role: SVG container — AlbersUSA projection, zoom, state fills/borders, nation outline
// Author: Dennies Bor

import { useRef, useMemo, createContext, useContext } from "react";
import * as d3 from "d3";
import * as topojson from "topojson-client";
import { useUsTopology } from "../../hooks/useUsTopology.js";
import { useZoom } from "../../hooks/useZoom.js";

const WIDTH = 960;
const HEIGHT = 600;

const MapContext = createContext(null);

export function useMapContext() {
  return useContext(MapContext);
}

export default function USMap({ children }) {
  const svgRef = useRef(null);
  const transform = useZoom(svgRef);

  const { data: topology, isPending, isError } = useUsTopology();

  const projection = useMemo(
    () =>
      d3
        .geoAlbersUsa()
        .scale(1300)
        .translate([WIDTH / 2, HEIGHT / 2]),
    [],
  );

  const geo = useMemo(() => {
    if (!topology) return null;
    return {
      // Individual state polygons — rendered as fills
      states: topojson.feature(topology, topology.objects.states),
      // Interior state borders only (a !== b filter drops the nation outline)
      borders: topojson.mesh(topology, topology.objects.states, (a, b) => a !== b),
      // Outer CONUS + AK + HI boundary from the nation object
      nation: topojson.feature(topology, topology.objects.nation),
    };
  }, [topology]);

  const path = useMemo(() => d3.geoPath().projection(projection), [projection]);

  return (
    <div className="w-full h-full">
      <svg
        ref={svgRef}
        viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
        preserveAspectRatio="xMidYMid meet"
        className="w-full h-full block cursor-grab active:cursor-grabbing select-none"
        style={{ background: "var(--color-surface)" }}
      >
        <MapContext.Provider value={{ projection, transform }}>
          <g transform={transform.toString()}>
            {/* State fills — subtle off-white so land reads differently from ocean */}
            {geo && (
              <path
                d={path(geo.states)}
                fill="#f1f5f9"
                stroke="none"
              />
            )}
            {/* Interior state borders */}
            {geo && (
              <path
                d={path(geo.borders)}
                fill="none"
                stroke="#cbd5e1"
                strokeWidth={0.5 / transform.k}
              />
            )}
            {/* Nation outline — heavier, defines CONUS/AK/HI edge clearly */}
            {geo && (
              <path
                d={path(geo.nation)}
                fill="none"
                stroke="#94a3b8"
                strokeWidth={1 / transform.k}
              />
            )}
            {children}
          </g>
        </MapContext.Provider>

        {isPending && (
          <text x={WIDTH / 2} y={HEIGHT / 2} textAnchor="middle" fontSize={14} fill="#94a3b8">
            Loading map…
          </text>
        )}
        {isError && (
          <text x={WIDTH / 2} y={HEIGHT / 2} textAnchor="middle" fontSize={14} fill="#ef4444">
            Failed to load topology
          </text>
        )}
      </svg>
    </div>
  );
}
