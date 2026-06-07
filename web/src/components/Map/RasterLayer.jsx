// Role: SVG image overlay for a pre-rendered EPSG:5070 hazard raster PNG
// Author: Dennies Bor
// Description: renders web/public/rasters/{hazard}.png as an <image> element
//   fitted to the 960x600 viewBox. The PNG was reprojected to EPSG:5070 with
//   a CONUS bbox matching D3's geoAlbersUsa at scale=1300 — so placing it at
//   x=0 y=0 width=960 height=600 aligns it with the vector layers without any
//   client-side coordinate math.

export default function RasterLayer({ hazard, rasterKey, opacity = 0.55 }) {
  if (!hazard) return null;
  const key = rasterKey ?? hazard;

  return (
    <image
      href={`/rasters/${key}.png`}
      x={0}
      y={0}
      width={960}
      height={600}
      preserveAspectRatio="none"
      opacity={opacity}
      style={{ pointerEvents: "none" }}
    />
  );
}
