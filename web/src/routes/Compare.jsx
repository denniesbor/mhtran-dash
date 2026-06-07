// Role: scientific summary page — paper figures, fragility curves, key findings
// Author: Dennies Bor

import { useEffect, useRef } from "react";
import Plotly from "plotly.js-dist-min";

// ─── Fragility parameters — HV substations, from utils/fragility.py ──────────
const DS_COLORS = {
  Slight:    "#92c5de",
  Moderate:  "#4393c3",
  Extensive: "#2166ac",
  Complete:  "#053061",
};

const FRAGILITY_HV = [
  {
    key: "earthquake", label: "Earthquake", imLabel: "PGA (g)",
    x: Array.from({ length: 300 }, (_, i) => 0.01 + i * (1.5 - 0.01) / 299),
    states: ["Slight", "Moderate", "Extensive", "Complete"],
    theta: [0.11, 0.15, 0.20, 0.47], beta: [0.50, 0.50, 0.50, 0.50],
    source: "HAZUS-MH via PNNL-33587",
  },
  {
    key: "flood", label: "Riverine flood", imLabel: "Flood depth (m)",
    x: Array.from({ length: 300 }, (_, i) => 0.01 + i * (6.0 - 0.01) / 299),
    states: ["Slight", "Moderate", "Extensive", "Complete"],
    theta: [0.5, 1.0, 1.5, 3.0], beta: [0.40, 0.40, 0.40, 0.40],
    source: "Sanchez-Munoz 2020 / PNNL-33587",
  },
  {
    key: "wind", label: "TC wind", imLabel: "Wind speed (m/s)",
    x: Array.from({ length: 300 }, (_, i) => 10 + i * (75 - 10) / 299),
    states: ["Slight", "Moderate", "Extensive", "Complete"],
    theta: [30, 42, 55, 67], beta: [0.25, 0.25, 0.25, 0.25],
    source: "HAZUS-MH4 / Watson 2020",
  },
  {
    key: "tornado", label: "Tornado", imLabel: "Wind speed (m/s)",
    x: Array.from({ length: 300 }, (_, i) => 30 + i * (110 - 30) / 299),
    states: ["Complete"],
    theta: [70], beta: [0.30],
    source: "Scenario",
  },
  {
    key: "wildfire", label: "Wildfire", imLabel: "WHP score",
    x: Array.from({ length: 300 }, (_, i) => i * 18000 / 299),
    states: ["Moderate"],
    theta: [10000], beta: [0.50],
    source: "USDA Dillon 2023 / Scenario",
  },
  {
    key: "hail", label: "Hail", imLabel: "Hail diameter (in)",
    x: Array.from({ length: 300 }, (_, i) => i * 5 / 299),
    states: ["Slight"],
    theta: [2.5], beta: [0.40],
    source: "Scenario",
  },
  {
    key: "lightning", label: "Lightning", imLabel: "Flash rate (fl/km²/yr)",
    x: Array.from({ length: 300 }, (_, i) => i * 30 / 299),
    states: ["Moderate"],
    theta: [10], beta: [0.50],
    source: "Scenario",
  },
  {
    key: "landslide", label: "Landslide", imLabel: "Susceptibility index",
    x: Array.from({ length: 300 }, (_, i) => i * 81 / 299),
    states: ["Complete"],
    theta: [60], beta: [0.50],
    source: "USGS Belair 2024 / Scenario",
  },
];

// ─── EAD data from paper abstract ────────────────────────────────────────────
const EAD_DIRECT = [
  { hazard: "Wildfire", direct: 3, economic: 0 },
  { hazard: "Hail",     direct: 5, economic: 0 },
  { hazard: "Freeze",   direct: 0, economic: 0 },
  { hazard: "Landslide",direct: 34, economic: 0 },
  { hazard: "Tornado",  direct: 42, economic: 4930 },
  { hazard: "Flood",    direct: 46, economic: 3590 },
  { hazard: "Earthquake",direct: 47, economic: 3020 },
  { hazard: "Lightning",direct: 87, economic: 0 },
  { hazard: "Wind",     direct: 137, economic: 0 },
  { hazard: "Geomag",   direct: 0, economic: 2070 },
];

// ─── Sub-components ───────────────────────────────────────────────────────────
function SectionHeading({ children }) {
  return (
    <h2 className="text-xl font-semibold text-ink mt-12 mb-4 pb-2 border-b border-line">
      {children}
    </h2>
  );
}

function StatCard({ value, label, sub }) {
  return (
    <div className="bg-white border border-line rounded-lg p-4 shadow-sm">
      <div className="text-2xl font-bold text-accent leading-tight">{value}</div>
      <div className="text-xs font-semibold text-ink mt-1">{label}</div>
      {sub && <div className="text-[11px] text-ink-muted mt-0.5">{sub}</div>}
    </div>
  );
}

function FigureCard({ src, caption, label }) {
  return (
    <figure className="bg-white border border-line rounded-lg overflow-hidden shadow-sm">
      <img src={src} alt={caption} className="w-full object-contain" loading="lazy" />
      <figcaption className="px-3 py-2 text-xs text-ink-muted border-t border-line">
        <span className="font-semibold text-ink">{label} &nbsp;</span>{caption}
      </figcaption>
    </figure>
  );
}

// ─── EAD bar chart ────────────────────────────────────────────────────────────
function EADChart() {
  const ref = useRef(null);

  useEffect(() => {
    if (!ref.current) return;
    const sorted = [...EAD_DIRECT].sort((a, b) => (a.direct + a.economic) - (b.direct + b.economic));

    Plotly.newPlot(
      ref.current,
      [
        {
          type: "bar", orientation: "h",
          name: "Direct damage (M$/day)",
          x: sorted.map(d => d.direct),
          y: sorted.map(d => d.hazard),
          marker: { color: "#2166ac" },
          hovertemplate: "%{y}: $%{x}M/day direct<extra></extra>",
        },
        {
          type: "bar", orientation: "h",
          name: "Economic output loss (M$/day)",
          x: sorted.map(d => d.economic / 1000),
          y: sorted.map(d => d.hazard),
          marker: { color: "#d6604d" },
          hovertemplate: "%{y}: $%{x:.2f}B/day economic<extra></extra>",
        },
      ],
      {
        barmode: "overlay",
        xaxis: {
          title: "Expected daily loss",
          type: "log",
          tickformat: "$,.0f",
          ticksuffix: "M",
          gridcolor: "#eee",
        },
        yaxis: { tickfont: { size: 11 } },
        legend: { orientation: "h", x: 0.5, xanchor: "center", y: -0.18, font: { size: 10 } },
        margin: { t: 10, b: 60, l: 100, r: 10 },
        paper_bgcolor: "white",
        plot_bgcolor: "white",
        height: 340,
      },
      { responsive: true, displayModeBar: false },
    );
    return () => { if (ref.current) Plotly.purge(ref.current); };
  }, []);

  return <div ref={ref} className="w-full" />;
}

// ─── Fragility parameter table ────────────────────────────────────────────────
function FragilityTable() {
  const rows = FRAGILITY_HV.flatMap(haz =>
    haz.states.map((ds, i) => ({
      hazard: haz.label, im: haz.imLabel, ds,
      theta: haz.theta[i], beta: haz.beta[i],
      source: haz.source,
    }))
  );

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-xs border-collapse">
        <thead>
          <tr className="bg-surface-inset">
            {["Hazard", "Intensity measure", "Damage state", "θ (median)", "β (log std)", "Source"].map(h => (
              <th key={h} className="text-left px-3 py-2 border-b border-line font-semibold text-ink">
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i} className={i % 2 === 0 ? "bg-white" : "bg-surface"}>
              <td className="px-3 py-1.5 border-b border-line font-medium text-ink">{r.hazard}</td>
              <td className="px-3 py-1.5 border-b border-line text-ink-muted font-mono">{r.im}</td>
              <td className="px-3 py-1.5 border-b border-line">
                <span className="px-1.5 py-0.5 rounded text-[10px] font-medium"
                  style={{ background: DS_COLORS[r.ds] + "22", color: DS_COLORS[r.ds] }}>
                  {r.ds}
                </span>
              </td>
              <td className="px-3 py-1.5 border-b border-line font-mono text-ink">{r.theta}</td>
              <td className="px-3 py-1.5 border-b border-line font-mono text-ink">{r.beta}</td>
              <td className="px-3 py-1.5 border-b border-line text-ink-muted">{r.source}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// ─── Main page ────────────────────────────────────────────────────────────────
export default function Compare() {
  return (
    <div className="h-full overflow-y-auto bg-surface">
      <div className="max-w-5xl mx-auto px-6 py-10 pb-20">

        {/* ── Hero ── */}
        <header className="mb-8">
          <div className="flex flex-wrap gap-2 mb-3">
            <a
              href="https://arxiv.org/abs/2605.23053"
              target="_blank" rel="noreferrer"
              className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-accent text-white text-xs font-medium hover:opacity-90 transition-opacity"
            >
              arXiv 2605.23053
            </a>
            <span className="inline-flex items-center px-3 py-1 rounded-full bg-surface-inset text-ink-muted text-xs font-medium">
              Preprint 2026
            </span>
          </div>
          <h1 className="text-2xl font-bold text-ink leading-snug mb-2">
            Multi-Hazard Risk Assessment of the US High-Voltage Transmission Network
          </h1>
          <p className="text-sm text-ink-muted">Dennies Bor · George Mason University</p>
          <p className="text-xs text-ink-muted mt-0.5">PhD Candidate, Earth Systems and Geoinformation Sciences</p>
        </header>

        {/* ── Abstract ── */}
        <SectionHeading>Abstract</SectionHeading>
        <div className="bg-white border border-line rounded-lg p-5 text-sm text-ink leading-relaxed space-y-3">
          <p>
            Modern economies depend critically on high-voltage power transmission networks.
            Yet this infrastructure is routinely disrupted by natural hazards ranging from earthquakes
            and floods to tornadoes and geomagnetic storms. Risk assessments have historically
            addressed hazards in isolation, leaving no common basis for comparing economic impacts
            across the full hazard portfolio.
          </p>
          <p>
            This study addresses this gap by developing an integrated framework linking hazard
            characterization, fragility modeling, and macroeconomic impact propagation. The framework
            is applied consistently across nine primary hazards and one compound freezing rain and
            wind gust hazard. Using national hazard datasets and a US high-voltage transmission
            network of over 13,000 line segments and 10,000 substations, we derive failure
            probabilities, expected damage, affected population, and downstream economic output losses.
          </p>
          <p>
            Among individual hazards, <strong>tropical cyclone wind</strong> produces the largest
            expected average daily damage at <strong>$137 M/day</strong>, followed by lightning
            at $87 M/day, earthquake at $47 M/day, flood at $46 M/day, tornado at $42 M/day, and
            landslide at $34 M/day. Downstream economic output losses are largest for tornado at
            <strong> $4.93 B/day</strong>, followed by flood at $3.59 B/day and earthquake at
            $3.02 B/day. A 250-year geomagnetic storm produces $2.07 B/day, placing space weather
            within the range of major terrestrial hazards. The compound freezing rain and wind gust
            scenario produces the largest stress-test disruption, affecting 237.4 M people and
            yielding a modeled downstream output loss of <strong>$85.16 B/day</strong>.
          </p>
          <p className="text-ink-muted italic">
            These results should be interpreted as first-order bounding estimates, with the compound
            scenario representing an upper-bound stress test. Overall, the framework establishes a
            consistent baseline for prioritizing investments in transmission network resilience.
          </p>
        </div>

        {/* ── Key findings ── */}
        <SectionHeading>Key Findings</SectionHeading>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
          <StatCard value="$137 M/day" label="TC Wind — direct damage" sub="Largest individual hazard" />
          <StatCard value="$87 M/day" label="Lightning — direct damage" sub="2nd highest individual" />
          <StatCard value="$4.93 B/day" label="Tornado — economic output loss" sub="Largest downstream impact" />
          <StatCard value="$2.07 B/day" label="Geomagnetic storm (250-yr)" sub="Space weather on par with terrestrial hazards" />
          <StatCard value="$85 B/day" label="Compound FZG — output loss" sub="Upper-bound stress test" />
          <StatCard value="237 M" label="People exposed — compound FZG" sub="Largest population disruption" />
          <StatCard value="13,000+" label="Transmission line segments" sub="US HV network scope" />
          <StatCard value="10,000+" label="Substations analyzed" sub="All voltage classes" />
        </div>

        {/* ── Network overview ── */}
        <SectionHeading>Network and Hazard Exposure</SectionHeading>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <FigureCard
            src="/figures/network_assets.png"
            label="Fig. 1"
            caption="US HV transmission network — substations and lines by voltage class."
          />
          <FigureCard
            src="/figures/multihazard_combined.png"
            label="Fig. 2"
            caption="Combined multi-hazard exposure map across all ten hazards."
          />
        </div>

        {/* ── Expected daily damage ── */}
        <SectionHeading>Expected Daily Damage by Hazard</SectionHeading>
        <div className="bg-white border border-line rounded-lg p-4 shadow-sm mb-4">
          <EADChart />
        </div>
        <FigureCard
          src="/figures/ead_by_hazard.png"
          label="Fig. 3"
          caption="Expected average daily damage (EAD) segmented into substation and line components, failed and exposed."
        />

        {/* ── Spatial EAD ── */}
        <SectionHeading>Spatial Distribution of Expected Damage</SectionHeading>
        <FigureCard
          src="/figures/spatial_ead.png"
          label="Fig. 4"
          caption="Spatial distribution of substation expected annual damage across CONUS. Each dot is one substation; color encodes annualised EAD."
        />

        {/* ── Population exposure ── */}
        <SectionHeading>Population Exposure</SectionHeading>
        <FigureCard
          src="/figures/pop_choropleth.png"
          label="Fig. 5"
          caption="County-level population served by substations exposed to each hazard. Shading indicates cumulative exposed population."
        />

        {/* ── Economic impact ── */}
        <SectionHeading>Downstream Economic Output Losses</SectionHeading>
        <FigureCard
          src="/figures/io_sector_loss_dodged.png"
          label="Fig. 6"
          caption="Sector-level economic output losses (input–output propagation). Bars show estimated output reduction per sector for each hazard scenario."
        />

        {/* ── Fragility curves ── */}
        <SectionHeading>Fragility Curves — HV Substations</SectionHeading>
        <p className="text-sm text-ink-muted mb-4">
          Lognormal P(DS ≥ ds | IM) curves for high-voltage substations across eight hazards.
          Damage states: Slight (5% DR), Moderate (20%), Extensive (50%), Complete (100%).
          Parameters derived from HAZUS-MH, PNNL-33587, and literature sources.
        </p>
        <FigureCard
          src="/figures/fragility_curves.png"
          label="Fig. 7"
          caption="Published fragility curves for HV substation components across eight natural hazards."
        />

        {/* ── Fragility parameter table ── */}
        <SectionHeading>Fragility Parameters — HV Substations</SectionHeading>
        <p className="text-sm text-ink-muted mb-3">
          Lognormal median (θ) and log standard deviation (β) for each damage state.
          DR = damage ratio applied to replacement cost.
        </p>
        <div className="bg-white border border-line rounded-lg shadow-sm overflow-hidden">
          <FragilityTable />
        </div>

        {/* ── Data & code ── */}
        <SectionHeading>Data &amp; Code</SectionHeading>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {[
            {
              label: "Paper",
              href: "https://arxiv.org/abs/2605.23053",
              desc: "arXiv preprint 2605.23053",
              icon: "📄",
            },
            {
              label: "Analysis code",
              href: "https://github.com/denniesbor/mhtran",
              desc: "GitHub: denniesbor/mhtran",
              icon: "💻",
            },
            {
              label: "Datasets",
              href: "https://zenodo.org/records/20331026",
              desc: "Zenodo archive 20331026",
              icon: "🗃️",
            },
          ].map(({ label, href, desc, icon }) => (
            <a
              key={label}
              href={href}
              target="_blank" rel="noreferrer"
              className="flex items-start gap-3 bg-white border border-line rounded-lg p-4 hover:border-accent transition-colors shadow-sm"
            >
              <span className="text-xl">{icon}</span>
              <div>
                <div className="text-sm font-semibold text-ink">{label}</div>
                <div className="text-xs text-ink-muted mt-0.5">{desc}</div>
              </div>
            </a>
          ))}
        </div>

        {/* ── Key data sources ── */}
        <SectionHeading>Key Data Sources</SectionHeading>
        <div className="bg-white border border-line rounded-lg overflow-hidden shadow-sm">
          <table className="w-full text-xs">
            <thead>
              <tr className="bg-surface-inset">
                <th className="text-left px-3 py-2 border-b border-line font-semibold text-ink">Hazard</th>
                <th className="text-left px-3 py-2 border-b border-line font-semibold text-ink">Dataset</th>
                <th className="text-left px-3 py-2 border-b border-line font-semibold text-ink">Source</th>
              </tr>
            </thead>
            <tbody>
              {[
                ["Earthquake", "2023 USGS National Seismic Hazard Model", "Petersen et al. 2024"],
                ["Flood", "Aqueduct Global Flood Model", "WRI / Reig et al. 2013"],
                ["Landslide", "USGS National Landslide Assessment", "Belair et al. 2024"],
                ["Wildfire", "USFS Wildfire Hazard Potential 2023", "Dillon 2023"],
                ["Wind (TC)", "STORM TC Dataset", "Bloemendaal et al. 2022"],
                ["Hail / Tornado", "NOAA SPC Storm Reports", "NOAA SPC 2024"],
                ["Lightning", "NASA LIS/OTD Climatology", "NASA ESDS 2024"],
                ["Freeze (FZG)", "SPIA-based Hazard Atlas", "Coburn et al. 2024"],
                ["Geomagnetic", "C-SWIM Framework", "Bor et al. (C-SWIM repo)"],
                ["Network", "HIFLD Transmission Lines + OSM", "HIFLD 2023, OSM 2024"],
              ].map(([hazard, dataset, source], i) => (
                <tr key={hazard} className={i % 2 === 0 ? "bg-white" : "bg-surface"}>
                  <td className="px-3 py-1.5 border-b border-line font-medium text-ink">{hazard}</td>
                  <td className="px-3 py-1.5 border-b border-line text-ink-muted">{dataset}</td>
                  <td className="px-3 py-1.5 border-b border-line text-ink-muted">{source}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <p className="text-[11px] text-ink-muted mt-8 text-center">
          Dashboard built with React + D3. Analysis code and datasets openly available under the{" "}
          <a href="https://github.com/denniesbor/mhtran" target="_blank" rel="noreferrer" className="text-accent hover:underline">
            mhtran repository
          </a>.
        </p>

      </div>
    </div>
  );
}
