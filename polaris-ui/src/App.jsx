import React from 'react';
import {
  AreaChart,
  DonutChart
} from '@tremor/react';

// 14-day Deep Arctic Winter slice (Jan 20 - Feb 02) during polar night (0 W solar)
// RHC defends the 20% floor: battery drains from ~44% to 20%, triggering sharp 48-50 kW bursts.
const winterTelemetryData = [
  { timestamp: "JAN 20", "Battery SOC (%)": 43.5, "Diesel Output (kW)": 0.0 },
  { timestamp: "JAN 21", "Battery SOC (%)": 20.0, "Diesel Output (kW)": 48.5 },
  { timestamp: "JAN 22", "Battery SOC (%)": 44.0, "Diesel Output (kW)": 0.0 },
  { timestamp: "JAN 23", "Battery SOC (%)": 20.0, "Diesel Output (kW)": 50.0 },
  { timestamp: "JAN 24", "Battery SOC (%)": 42.8, "Diesel Output (kW)": 0.0 },
  { timestamp: "JAN 25", "Battery SOC (%)": 20.0, "Diesel Output (kW)": 47.5 },
  { timestamp: "JAN 26", "Battery SOC (%)": 44.2, "Diesel Output (kW)": 0.0 },
  { timestamp: "JAN 27", "Battery SOC (%)": 20.0, "Diesel Output (kW)": 49.0 },
  { timestamp: "JAN 28", "Battery SOC (%)": 43.1, "Diesel Output (kW)": 0.0 },
  { timestamp: "JAN 29", "Battery SOC (%)": 20.0, "Diesel Output (kW)": 50.0 },
  { timestamp: "JAN 30", "Battery SOC (%)": 44.5, "Diesel Output (kW)": 0.0 },
  { timestamp: "JAN 31", "Battery SOC (%)": 20.0, "Diesel Output (kW)": 48.0 },
  { timestamp: "FEB 01", "Battery SOC (%)": 43.8, "Diesel Output (kW)": 0.0 },
  { timestamp: "FEB 02", "Battery SOC (%)": 20.0, "Diesel Output (kW)": 49.5 },
];

const curtailmentData = [
  { cause: "Storage Saturation (Battery @ 95%)", kwh: 17031, share: "72.0%", code: "CURT-01" },
  { cause: "Inverter Power Limits", kwh: 4257, share: "18.0%", code: "CURT-02" },
  { cause: "Policy Reserve Headroom", kwh: 2365, share: "10.0%", code: "CURT-03" },
];

const benchmarkMatrix = [
  {
    channel: "SYS.FUEL.01",
    metric: "TOTAL ANNUAL DIESEL CONSUMED",
    baseline: "68,999 L",
    rhc: "693 L",
    delta: "↓ 99.0% (-68,306 L)",
    deltaStatus: "positive",
  },
  {
    channel: "FIN.OPEX.02",
    metric: "ANNUAL FUEL COST AVOIDED (@ €1.80/L)",
    baseline: "€124,198",
    rhc: "€1,247",
    delta: "+€122,951 NET SAVINGS",
    deltaStatus: "positive",
  },
  {
    channel: "ENG.WEAR.03",
    metric: "GENERATOR RUNTIME (MECHANICAL WEAR)",
    baseline: "6,944 HRS",
    rhc: "91 HRS",
    delta: "↓ 6,853 HRS AVOIDED (-98.7%)",
    deltaStatus: "positive",
  },
  {
    channel: "ENV.EMIS.04",
    metric: "DIRECT CO2 EQUIVALENT EMISSIONS",
    baseline: "182.85 TONS",
    rhc: "1.84 TONS",
    delta: "↓ 181.01 TONS CO2e (-99.0%)",
    deltaStatus: "positive",
  },
  {
    channel: "GRID.RELI.05",
    metric: "SYSTEM RELIABILITY & CRITICAL UPTIME",
    baseline: "99.80% (LOAD SHEDDING RISK)",
    rhc: "100.00% (0.00 kWh UNMET)",
    delta: "ZERO OUTAGES [PERFECT UPTIME]",
    deltaStatus: "positive",
  },
];

/* -------------------------------------------------------------------------- */
/*  Presentation helpers (styling only: no data changes)                      */
/* -------------------------------------------------------------------------- */

// Fonts + Tremor/Recharts overrides. Scoped to .polaris-* so nothing leaks.
// Tip: move the @import into index.html as <link> tags for faster first paint.
const DASHBOARD_CSS = `
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&family=Geist+Mono:wght@400;500;600&family=Inter:wght@400;500;600&display=swap');

:root { color-scheme: dark; }

/* Hero chart: faint dashed grid, mono ticks */
.polaris-chart .recharts-cartesian-grid line { stroke-dasharray: 2 6; }
.polaris-chart .recharts-cartesian-axis-tick-value,
.polaris-chart text { font-family: 'Geist Mono', ui-monospace, monospace; font-size: 11px; fill: #71717a; }

/* Battery SOC: deep cyan wash fading to transparent */
.polaris-chart linearGradient stop:first-child { stop-opacity: 0.55; }
.polaris-chart .recharts-area[class*="stroke-cyan"] .recharts-area-curve {
  stroke: #22d3ee; stroke-width: 2;
  filter: drop-shadow(0 0 6px rgba(34,211,238,0.55));
}

/* Diesel bursts: sharp, high-opacity red, barely any fill */
.polaris-chart .recharts-area[class*="stroke-rose"] .recharts-area-curve {
  stroke: #f43f5e; stroke-width: 2.25; stroke-linejoin: miter;
  filter: drop-shadow(0 0 5px rgba(244,63,94,0.75));
}
.polaris-chart .recharts-area[class*="stroke-rose"] .recharts-area-area { fill: rgba(244,63,94,0.06) !important; }

/* Donut: slim gaps between segments, soft ambient glow */
.polaris-donut .recharts-pie-sector path,
.polaris-donut .recharts-sector { stroke: #09090b; stroke-width: 3; }
.polaris-donut .recharts-pie { filter: drop-shadow(0 0 14px rgba(129,140,248,0.22)); }
.polaris-donut text { font-family: 'Geist Mono', ui-monospace, monospace; }
`;

// Glass surface used by every major card
const PANEL =
  "relative rounded-2xl border border-white/10 bg-zinc-900/50 backdrop-blur-xl shadow-panel " +
  "before:pointer-events-none before:absolute before:inset-x-8 before:top-0 before:h-px " +
  "before:bg-gradient-to-r before:from-transparent before:via-white/25 before:to-transparent";

const PILL_STYLES = {
  positive:
    "border-emerald-400/25 bg-emerald-400/10 text-emerald-300 shadow-[0_0_18px_-6px_rgba(52,211,153,0.7)]",
  warning:
    "border-amber-400/25 bg-amber-400/10 text-amber-300 shadow-[0_0_18px_-6px_rgba(251,191,36,0.6)]",
  negative:
    "border-rose-400/25 bg-rose-400/10 text-rose-300 shadow-[0_0_18px_-6px_rgba(244,63,94,0.7)]",
};

const SERIES_STYLE = {
  "Battery SOC (%)": { dot: "bg-cyan-400 shadow-[0_0_8px_rgba(34,211,238,0.9)]", unit: "%" },
  "Diesel Output (kW)": { dot: "bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.9)]", unit: " kW" },
};

const CURTAILMENT_COLORS = ["indigo", "violet", "cyan"];
const CURTAILMENT_SWATCH = [
  { dot: "bg-indigo-500", bar: "from-indigo-600 to-indigo-400" },
  { dot: "bg-violet-500", bar: "from-violet-600 to-violet-400" },
  { dot: "bg-cyan-400", bar: "from-cyan-500 to-cyan-300" },
];

function LiveDot() {
  return (
    <span className="relative flex h-2 w-2">
      <span className="absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-60 motion-safe:animate-ping" />
      <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-400 shadow-[0_0_10px_rgba(52,211,153,0.9)]" />
    </span>
  );
}

// Hardware-tag style chip: small sans label, mono value
function SpecTag({ label, value, dot }) {
  return (
    <div className="inline-flex items-center gap-2 rounded-md border border-white/10 bg-white/[0.03] px-2.5 py-1.5 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.04)]">
      {dot && <span className={`h-1.5 w-1.5 rounded-full ${dot}`} />}
      <span className="text-[11px] text-zinc-500">{label}</span>
      <span className="font-mono text-[12px] font-medium text-zinc-100">{value}</span>
    </div>
  );
}

// Glass tooltip for the hero chart
function TelemetryTooltip({ active, payload, label }) {
  if (!active || !payload || !payload.length) return null;
  return (
    <div className="min-w-[10rem] rounded-lg border border-white/10 bg-zinc-950/90 px-3 py-2.5 shadow-2xl backdrop-blur-md">
      <p className="mb-2 font-mono text-[11px] text-zinc-500">{label}</p>
      <div className="space-y-1.5">
        {payload.map((item, i) => {
          const key = item.dataKey || item.name || item.category;
          const style = SERIES_STYLE[key] || { dot: "bg-zinc-400", unit: "" };
          return (
            <div key={`${key}-${i}`} className="flex items-center justify-between gap-6">
              <span className="flex items-center gap-2 text-xs text-zinc-400">
                <span className={`h-1.5 w-1.5 rounded-full ${style.dot}`} />
                {String(key).replace(/\s*\(.*\)/, "")}
              </span>
              <span className="font-mono text-xs font-medium text-white">
                {Number(item.value).toFixed(1)}
                {style.unit}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

const gradientNumber =
  "font-mono text-4xl xl:text-[2.6rem] font-semibold leading-none tracking-tight tabular-nums " +
  "bg-clip-text text-transparent";

export default function PolarisDashboard() {
  const kpis = [
    {
      label: "Total diesel consumed",
      value: "693 L",
      dot: "bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.8)]",
      badge: "↓ 99.0% vs reactive baseline",
      foot: [["Baseline", "68,999 L"], ["Avoided", "68,306 L"]],
    },
    {
      label: "Fuel cost avoided",
      value: "~€122,950",
      hero: true,
      dot: "bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.9)]",
      badge: "68,306 L saved annually",
      foot: [["Remote Arctic parity", "€1.80 / liter"]],
    },
    {
      label: "Generator wear",
      value: "91 hours",
      dot: "bg-amber-400 shadow-[0_0_8px_rgba(251,191,36,0.8)]",
      badge: "↓ 6,853 hours avoided",
      foot: [["Baseline", "6,944 hrs"], ["Overhaul", ">8.5 yrs"]],
    },
    {
      label: "System reliability",
      value: "100% uptime",
      dot: "bg-cyan-400 shadow-[0_0_8px_rgba(34,211,238,0.9)]",
      badge: "0.00 kWh unmet load",
      foot: [["Critical deficit", "0.00%"], ["Blackouts", "Zero"]],
    },
  ];

  return (
    <div className="dark relative min-h-screen bg-zinc-950 font-sans text-zinc-100 antialiased selection:bg-cyan-400/30 selection:text-white">
      <style>{DASHBOARD_CSS}</style>

      {/* Layered background depth: aurora washes + faint engineering grid */}
      <div aria-hidden className="pointer-events-none fixed inset-0 bg-aurora" />
      <div
        aria-hidden
        className="pointer-events-none fixed inset-0 bg-grid-faint bg-[size:56px_56px] [mask-image:radial-gradient(ellipse_at_top,black,transparent_70%)]"
      />

      <div className="relative z-10">
        {/* ------------------------------ HEADER ------------------------------ */}
        <header className="sticky top-0 z-30 border-b border-white/10 bg-zinc-950/70 backdrop-blur-xl">
          <div className="mx-auto flex max-w-[1600px] flex-col gap-4 px-4 py-4 sm:px-6 lg:flex-row lg:items-center lg:justify-between lg:px-8">
            <div className="flex items-center gap-4">
              <div className="grid h-10 w-10 shrink-0 place-items-center rounded-xl border border-white/10 bg-gradient-to-br from-cyan-400/20 to-indigo-500/20 shadow-glow-cyan">
                <svg viewBox="0 0 24 24" className="h-5 w-5 text-cyan-300" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="8.5" />
                  <path d="M12 3.5v17M3.5 12h17" opacity=".45" />
                  <path d="M12 7l3.2 5L12 17l-3.2-5z" fill="currentColor" fillOpacity=".3" />
                </svg>
              </div>
              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-x-3 gap-y-1.5">
                  <h1 className="text-[15px] font-semibold tracking-tight text-white">POLARIS N6</h1>
                  <span className="inline-flex items-center gap-2 rounded-full border border-emerald-400/25 bg-emerald-400/10 px-2.5 py-1 text-[11px] font-medium tracking-wider text-emerald-300">
                    <LiveDot />
                    SYSTEM ACTIVE
                  </span>
                  <span className="text-xs text-zinc-500">Mt. Nuolja · RHC simulation</span>
                </div>
                <p className="mt-1.5 font-mono text-[11px] text-zinc-500">
                  Telemetry matrix ARCTIC-01
                  <span className="mx-2 text-zinc-700">/</span>68.3582°N, 18.7838°E
                  <span className="mx-2 text-zinc-700">/</span>1,160 m
                  <span className="mx-2 text-zinc-700">/</span>8,760 h horizon
                  <span className="mx-2 text-zinc-700">/</span>QP-MILP
                </p>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <SpecTag label="Storage" value="200 kWh LiFePO4" dot="bg-cyan-400 shadow-[0_0_8px_rgba(34,211,238,0.8)]" />
              <SpecTag label="Solar PV" value="120 kW bifacial" dot="bg-amber-400 shadow-[0_0_8px_rgba(251,191,36,0.7)]" />
              <SpecTag label="Backup" value="50 kW diesel" dot="bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.8)]" />
              <div className="inline-flex items-center gap-2 rounded-md border border-emerald-400/25 bg-emerald-400/10 px-2.5 py-1.5 text-[12px] font-medium text-emerald-300">
                <svg viewBox="0 0 16 16" className="h-3.5 w-3.5" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M3 8.5l3.2 3L13 4.5" /></svg>
                100% autonomous
              </div>
            </div>
          </div>
        </header>

        <main className="mx-auto max-w-[1600px] space-y-8 px-4 py-8 sm:px-6 lg:px-8">
          {/* ----------------------------- KPI RIBBON ---------------------------- */}
          <section>
            <div className="mb-3 flex flex-col gap-1 sm:flex-row sm:items-end sm:justify-between">
              <h2 className="text-[15px] font-semibold tracking-tight text-zinc-50">Executive KPIs: model ROI audit</h2>
              <p className="text-xs text-zinc-500">Compared against a heuristic, reactive rule-based engine</p>
            </div>

            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
              {kpis.map((kpi) => (
                <div key={kpi.label} className="relative">
                  {kpi.hero && (
                    <div
                      aria-hidden
                      className="absolute -inset-3 rounded-[28px] bg-emerald-400/20 opacity-70 blur-2xl"
                    />
                  )}
                  <div
                    className={`${PANEL} flex h-full flex-col justify-between p-5 ${
                      kpi.hero ? "border-emerald-400/30 bg-zinc-900/70" : ""
                    }`}
                  >
                    <div>
                      <div className="flex items-center gap-2">
                        <span className={`h-1.5 w-1.5 rounded-full ${kpi.dot}`} />
                        <span className="text-xs font-medium text-zinc-400">{kpi.label}</span>
                      </div>
                      <div
                        className={`mt-4 ${gradientNumber} ${
                          kpi.hero
                            ? "bg-gradient-to-br from-white via-emerald-100 to-emerald-300 drop-shadow-[0_0_22px_rgba(52,211,153,0.35)]"
                            : "bg-gradient-to-b from-white to-zinc-400"
                        }`}
                      >
                        {kpi.value}
                      </div>
                    </div>

                    <div className="mt-6">
                      <span
                        className={`inline-flex items-center rounded-full border px-2.5 py-1 font-mono text-[11px] font-medium ${PILL_STYLES.positive}`}
                      >
                        {kpi.badge}
                      </span>
                      <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 border-t border-white/5 pt-3">
                        {kpi.foot.map(([k, v]) => (
                          <span key={k} className="text-[11px] text-zinc-500">
                            {k} <span className="ml-1 font-mono text-zinc-300">{v}</span>
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* ------------------------ TELEMETRY + DIAGNOSTICS -------------------- */}
          <section className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            {/* Hero chart */}
            <div className={`${PANEL} flex flex-col p-6 lg:col-span-2`}>
              <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <h2 className="text-[15px] font-semibold tracking-tight text-zinc-50">
                    Deep winter telemetry
                  </h2>
                  <p className="mt-1 text-xs text-zinc-500">
                    Jan 20 – Feb 02 · polar night (0.0 W/m² irradiance) · 20.0% minimum SOC enforced
                  </p>
                </div>
                <div className="flex items-center gap-4 text-xs text-zinc-300">
                  <span className="flex items-center gap-2">
                    <span className="h-2 w-2 rounded-full bg-cyan-400 shadow-[0_0_10px_rgba(34,211,238,0.9)]" />
                    Battery SOC (%)
                  </span>
                  <span className="flex items-center gap-2">
                    <span className="h-2 w-2 rounded-full bg-rose-500 shadow-[0_0_10px_rgba(244,63,94,0.9)]" />
                    Diesel gen (kW)
                  </span>
                </div>
              </div>

              <div className="mt-4 rounded-xl border border-white/10 bg-gradient-to-br from-cyan-400/[0.07] via-transparent to-transparent p-4 text-[13px] leading-relaxed text-zinc-400">
                <span className="mr-2 font-medium text-cyan-300">Controller logic</span>
                Continuous diesel idling at low loads (10-15 kW) is locked out. RHC cycles the battery strictly between
                <span className="font-mono text-white"> 20.0% and 44.5% SOC</span>. At the 20.0% floor the controller fires a
                high-efficiency <span className="font-mono text-rose-400">50 kW pulse</span> at peak Brake Thermal Efficiency (BTE) to
                rapid-charge storage, cutting fuel the moment it recharges.
              </div>

              <div className="polaris-chart mt-5">
                <AreaChart
                  className="h-80 w-full"
                  data={winterTelemetryData}
                  index="timestamp"
                  categories={["Battery SOC (%)", "Diesel Output (kW)"]}
                  colors={["cyan", "rose"]}
                  showGradient={true}
                  curveType="linear"
                  showAnimation={true}
                  animationDuration={1400}
                  yAxisWidth={40}
                  minValue={0}
                  maxValue={60}
                  showGridLines={true}
                  showLegend={false}
                  valueFormatter={(val) => `${val}`}
                  customTooltip={TelemetryTooltip}
                />
              </div>

              <div className="mt-5 grid grid-cols-1 gap-3 sm:grid-cols-3">
                {[
                  ["Min SOC floor", "20.0%", "text-cyan-300"],
                  ["BTE sweet spot", "50.0 kW", "text-rose-400"],
                  ["Unmet demand", "0.00 kWh", "text-emerald-300"],
                ].map(([k, v, c]) => (
                  <div key={k} className="rounded-lg border border-white/10 bg-white/[0.03] px-3.5 py-2.5">
                    <div className="text-[11px] text-zinc-500">{k}</div>
                    <div className={`mt-0.5 font-mono text-sm font-semibold ${c}`}>{v}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Curtailment diagnostics */}
            <div className={`${PANEL} flex flex-col p-6`}>
              <div>
                <h2 className="text-[15px] font-semibold tracking-tight text-zinc-50">
                  Summer curtailment diagnostics
                </h2>
                <p className="mt-1 text-xs text-zinc-500">
                  23.6 MWh of renewable solar energy spilled (midnight sun regime)
                </p>
              </div>

              <div className="polaris-donut mt-5">
                <DonutChart
                  className="h-48 w-full"
                  data={curtailmentData}
                  category="kwh"
                  index="cause"
                  label="23.6 MWh"
                  valueFormatter={(number) => `${(number / 1000).toFixed(1)} MWh`}
                  colors={CURTAILMENT_COLORS}
                  showAnimation={true}
                />
              </div>

              <div className="mt-5 space-y-2.5">
                {curtailmentData.map((item, i) => (
                  <div key={item.code} className="rounded-lg border border-white/10 bg-white/[0.03] p-3">
                    <div className="flex items-center justify-between gap-3">
                      <span className="flex min-w-0 items-center gap-2 text-xs text-zinc-300">
                        <span className={`h-2 w-2 shrink-0 rounded-full ${CURTAILMENT_SWATCH[i].dot}`} />
                        <span className="truncate">{item.cause}</span>
                      </span>
                      <span className="shrink-0 font-mono text-xs font-medium text-white">
                        {(item.kwh / 1000).toFixed(1)} MWh
                      </span>
                    </div>
                    <div className="mt-2.5 h-1 overflow-hidden rounded-full bg-white/5">
                      <div
                        className={`h-full rounded-full bg-gradient-to-r ${CURTAILMENT_SWATCH[i].bar}`}
                        style={{ width: item.share }}
                      />
                    </div>
                    <div className="mt-2 flex justify-between font-mono text-[10px] text-zinc-500">
                      <span>{item.code}</span>
                      <span className="text-zinc-300">{item.share}</span>
                    </div>
                  </div>
                ))}
              </div>

              {/* Hardware insight: recommendation callout with glowing border */}
              <div className="relative mt-6">
                <div
                  aria-hidden
                  className="absolute -inset-0.5 rounded-2xl bg-gradient-to-br from-violet-500/40 via-indigo-500/20 to-cyan-400/40 blur-md motion-safe:animate-breathe"
                />
                <div className="relative rounded-xl bg-gradient-to-br from-violet-400/60 via-indigo-400/20 to-cyan-300/50 p-px">
                  <div className="rounded-[11px] bg-zinc-950/95 p-4">
                    <div className="flex items-center justify-between">
                      <span className="flex items-center gap-2 text-xs font-medium text-violet-300">
                        <svg viewBox="0 0 24 24" className="h-4 w-4" fill="currentColor"><path d="M12 2l1.9 5.6L19.5 9.5l-5.6 1.9L12 17l-1.9-5.6L4.5 9.5l5.6-1.9L12 2zm7 12l.9 2.6 2.6.9-2.6.9L19 21l-.9-2.6-2.6-.9 2.6-.9L19 14z" /></svg>
                        Hardware insight
                      </span>
                      <span className="rounded-full border border-violet-400/30 bg-violet-400/10 px-2 py-0.5 text-[10px] font-medium text-violet-300">
                        Recommended
                      </span>
                    </div>
                    <p className="mt-2.5 text-[13px] leading-relaxed text-zinc-400">
                      Upgrading the 200 kWh battery to <span className="font-mono font-semibold text-white">350 kWh</span> captures
                      this wasted solar energy. Adding 150 kWh of storage eliminates{" "}
                      <span className="font-mono font-semibold text-violet-300">72.0% (17,031 kWh)</span> of current summer
                      curtailment, storing zero-carbon midnight-sun energy to offset autumn diesel consumption.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* --------------------------- BENCHMARK TABLE ------------------------- */}
          <section className={`${PANEL} overflow-hidden`}>
            <div className="flex flex-col gap-3 border-b border-white/10 p-6 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h2 className="text-[15px] font-semibold tracking-tight text-zinc-50">Annual benchmark matrix</h2>
                <p className="mt-1 text-xs text-zinc-500">
                  POLARIS RHC model vs reactive rule-based baseline · 8,760 hourly closed-loop timesteps · Nuolja Arctic data parity
                </p>
              </div>
              <span className="inline-flex w-fit items-center gap-1.5 rounded-full border border-emerald-400/25 bg-emerald-400/10 px-3 py-1 text-[11px] font-medium text-emerald-300 shadow-[0_0_18px_-6px_rgba(52,211,153,0.7)]">
                <svg viewBox="0 0 16 16" className="h-3.5 w-3.5" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M3 8.5l3.2 3L13 4.5" /></svg>
                Verified by model audit
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full min-w-[960px] border-collapse text-left text-[13px]">
                <thead>
                  <tr className="border-b border-white/10 bg-white/[0.03] text-xs font-medium text-zinc-500">
                    <th className="px-6 py-3.5 font-medium">Channel</th>
                    <th className="px-6 py-3.5 font-medium">System parameter</th>
                    <th className="px-6 py-3.5 font-medium">Reactive baseline</th>
                    <th className="px-6 py-3.5 font-medium text-cyan-300">POLARIS RHC (ML model)</th>
                    <th className="px-6 py-3.5 font-medium text-emerald-300">Impact &amp; strategic ROI</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {benchmarkMatrix.map((row) => (
                    <tr key={row.channel} className="transition-colors hover:bg-zinc-800/50">
                      <td className="px-6 py-4">
                        <span className="rounded-md border border-white/10 bg-white/[0.03] px-2 py-1 font-mono text-[11px] text-zinc-400">
                          {row.channel}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-xs font-medium tracking-wide text-zinc-200">{row.metric}</td>
                      <td className="px-6 py-4 font-mono text-zinc-500">{row.baseline}</td>
                      <td className="px-6 py-4 font-mono text-sm font-semibold text-white">{row.rhc}</td>
                      <td className="px-6 py-4">
                        <span
                          className={`inline-flex items-center rounded-full border px-3 py-1 font-mono text-xs font-medium ${
                            PILL_STYLES[row.deltaStatus] || PILL_STYLES.positive
                          }`}
                        >
                          {row.delta}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          {/* ------------------------------ FOOTER ------------------------------ */}
          <footer className="flex flex-col items-center justify-between gap-2 border-t border-white/10 pt-5 pb-2 text-[11px] text-zinc-600 sm:flex-row">
            <span>POLARIS microgrid control system · v4.2.8 · receding horizon controller</span>
            <span className="flex items-center gap-2">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-400/80" />
              System integrity 100% nominal · zero logical errors detected
            </span>
          </footer>
        </main>
      </div>
    </div>
  );
}
