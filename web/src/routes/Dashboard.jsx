// Role: main map view — single hazard, full CONUS
// Author: Dennies Bor

import { useState, useCallback } from "react";
import { useSearchParams } from "react-router-dom";
import USMap from "../components/Map/USMap.jsx";
import SubstationLayer from "../components/Map/SubstationLayer.jsx";
import LineLayer from "../components/Map/LineLayer.jsx";
import RasterLayer from "../components/Map/RasterLayer.jsx";
import RasterLegend from "../components/Map/RasterLegend.jsx";
import HazardSelector from "../components/controls/HazardSelector.jsx";
import HazardLegend from "../components/Map/HazardLegend.jsx";
import StatsPanel from "../components/Map/StatsPanel.jsx";
import Tooltip from "../components/Tooltip.jsx";
import { useSubstations } from "../hooks/useSubstations.js";
import { useLines } from "../hooks/useLines.js";
import { useColorScale } from "../hooks/useColorScale.js";
import { DEFAULT_HAZARD, LINE_HAZARDS, RASTER_HAZARDS } from "../lib/constants.js";

export default function Dashboard() {
  const [searchParams] = useSearchParams();
  const hazard = searchParams.get("hazard") ?? DEFAULT_HAZARD;
  const lineHazard = LINE_HAZARDS.has(hazard) ? hazard : null;

  const { data: subData, isPending: subsPending } = useSubstations(hazard);
  const { data: lineData, isPending: linesPending } = useLines(lineHazard);

  const subFeatures = subData?.features ?? [];
  const lineFeatures = lineData?.features ?? [];

  const subsColorScale = useColorScale(subFeatures, hazard);
  const linesColorScale = useColorScale(lineFeatures, lineHazard);

  const [tooltip, setTooltip] = useState(null);
  const [showRaster, setShowRaster] = useState(true);
  const hasRaster = RASTER_HAZARDS.has(hazard);

  // geomag-specific raster variant: E/B field × 100/250yr return period
  const [geomag, setGeomag] = useState({ field: "E", rp: 100 });
  const rasterKey = hazard === "geomag" ? `geomag_${geomag.field}_${geomag.rp}` : hazard;

  const handleHover = useCallback((data, event) => {
    setTooltip({ ...data, x: event.clientX, y: event.clientY });
  }, []);

  const handleLeave = useCallback(() => setTooltip(null), []);

  return (
    <div className="h-full w-full relative">
      <USMap>
        {/* Raster intensity layer sits below the vector layers */}
        {hasRaster && showRaster && <RasterLayer hazard={hazard} rasterKey={rasterKey} />}

        {!linesPending && (
          <LineLayer
            features={lineFeatures}
            hazard={lineHazard}
            colorScale={linesColorScale}
            onHover={handleHover}
            onLeave={handleLeave}
          />
        )}
        {!subsPending && (
          <SubstationLayer
            features={subFeatures}
            hazard={hazard}
            colorScale={subsColorScale}
            onHover={handleHover}
            onLeave={handleLeave}
          />
        )}
      </USMap>

      <HazardSelector
        hasRaster={hasRaster}
        showRaster={showRaster}
        onToggleRaster={() => setShowRaster(v => !v)}
        geomag={hazard === "geomag" ? geomag : null}
        onGeomagChange={setGeomag}
      />
      <StatsPanel subFeatures={subFeatures} lineFeatures={lineFeatures} hazard={hazard} geomag={hazard === "geomag" ? geomag : null} />
      <HazardLegend colorScale={subsColorScale} hazard={hazard} />
      <RasterLegend hazard={hazard} rasterKey={rasterKey} showRaster={showRaster} />
      <Tooltip tooltip={tooltip} />
    </div>
  );
}
