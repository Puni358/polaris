/**
 * POLARIS Industrial SCADA HMI Application Script
 * Vanilla ES6 JavaScript handling navigation, API data fetching, telemetry rendering,
 * and SVG engineering trend visualizations.
 */

document.addEventListener("DOMContentLoaded", () => {
  initNavigation();
  initScenarioSelector();
  fetchHMIData();
});

// NAVIGATION LOGIC
function initNavigation() {
  const navBtns = document.querySelectorAll(".nav-btn");
  const screens = document.querySelectorAll(".screen-panel");

  navBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      const targetId = btn.getAttribute("data-screen");

      navBtns.forEach(b => b.classList.remove("active"));
      screens.forEach(s => s.classList.remove("active"));

      btn.classList.add("active");
      const targetScreen = document.getElementById(targetId);
      if (targetScreen) {
        targetScreen.classList.add("active");
      }
    });
  });
}

// SCENARIO SELECTOR LOGIC
function initScenarioSelector() {
  const scenCards = document.querySelectorAll(".scenario-card");
  let selectedScenario = "demo_scenario.json";

  scenCards.forEach(card => {
    card.addEventListener("click", () => {
      scenCards.forEach(c => c.classList.remove("active"));
      card.classList.add("active");
      selectedScenario = card.getAttribute("data-scenario");
    });
  });

  const runBtn = document.getElementById("btn-run-scenario");
  if (runBtn) {
    runBtn.addEventListener("click", () => {
      runBtn.innerText = "EXECUTING PIPELINE...";
      runBtn.disabled = true;

      fetch("/api/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scenario: selectedScenario, steps: 24 })
      })
      .then(res => res.json())
      .then(data => {
        runBtn.innerText = "RUN SELECTED SCENARIO PIPELINE";
        runBtn.disabled = false;
        fetchHMIData(); // Refresh all telemetry views
      })
      .catch(err => {
        console.error("Scenario execution error:", err);
        runBtn.innerText = "RUN SELECTED SCENARIO PIPELINE";
        runBtn.disabled = false;
      });
    });
  }
}

// FETCH AUTHORITATIVE RUNTIME ARTIFACTS
function fetchHMIData() {
  let forecastData = null;
  let dispatchData = null;

  // 1. Fetch Status / Run Report and Governance Metadata
  Promise.all([
    fetch("/api/status").then(res => res.json()).catch(err => ({ error: err.message })),
    fetch("/api/governance").then(res => res.json()).catch(err => ({ error: err.message }))
  ]).then(([report, gov]) => {
    renderStatusReport(report);
    renderAnalyticsReport(report, gov);
  });

  // 2. Fetch Forecast Bundle
  fetch("/api/forecast")
    .then(res => res.json())
    .then(bundle => {
      forecastData = bundle;
      renderForecastBundle(bundle);
      if (dispatchData) {
        renderOverviewTrend(forecastData, dispatchData);
      }
    })
    .catch(err => console.error("Error fetching forecast:", err));

  // 3. Fetch Dispatch Plan
  fetch("/api/dispatch")
    .then(res => res.json())
    .then(plan => {
      dispatchData = plan;
      renderDispatchPlan(plan);
      renderDigitalTwinSOCTrend(plan);
      if (forecastData) {
        renderOverviewTrend(forecastData, dispatchData);
      }
    })
    .catch(err => console.error("Error fetching dispatch:", err));
}

// RENDER ANALYTICS REPORT (SCREEN 08 DYNAMIC BINDING)
function renderAnalyticsReport(report, govData) {
  if (!report || report.error) {
    const el = document.getElementById("rep-diesel-fuel");
    if (el) el.innerText = "unavailable";
    return;
  }

  const ems = report.ems_evaluation || {};
  const forecast = report.forecast_evaluation || {};
  const solarMetrics = forecast.solar_irradiance_metrics || {};

  // Layer 1 Physical Fuel
  const dFuelEl = document.getElementById("rep-diesel-fuel");
  if (dFuelEl) {
    dFuelEl.innerText = ems.total_diesel_fuel_liters !== undefined 
      ? `${ems.total_diesel_fuel_liters.toFixed(2)} Liters (Physical)` 
      : "unavailable";
  }

  // Layer 2 Economic Fuel Equivalent
  const eFuelEl = document.getElementById("rep-economic-fuel");
  if (eFuelEl) {
    eFuelEl.innerText = "unavailable / not verified in legacy artifact";
  }

  // Diesel Energy Output
  const dEnergyEl = document.getElementById("rep-diesel-energy");
  if (dEnergyEl) {
    dEnergyEl.innerText = ems.total_diesel_energy_kwh !== undefined 
      ? `${ems.total_diesel_energy_kwh.toFixed(2)} kWh` 
      : "unavailable";
  }

  // Renewable Energy Used
  const renUsedEl = document.getElementById("rep-ren-used");
  if (renUsedEl) {
    renUsedEl.innerText = ems.total_renewable_energy_used_kwh !== undefined 
      ? `${ems.total_renewable_energy_used_kwh.toFixed(2)} kWh` 
      : "unavailable";
  }

  // Renewable Curtailment
  const renCurtEl = document.getElementById("rep-ren-curt");
  if (renCurtEl) {
    if (ems.total_renewable_curtailment_kwh !== undefined && ems.renewable_curtailment_pct !== undefined) {
      renCurtEl.innerText = `${ems.total_renewable_curtailment_kwh.toFixed(2)} kWh (${ems.renewable_curtailment_pct.toFixed(2)}%)`;
    } else {
      renCurtEl.innerText = "unavailable";
    }
  }

  // Renewable Utilization Rate
  const renUtilEl = document.getElementById("rep-ren-util");
  if (renUtilEl) {
    renUtilEl.innerText = ems.renewable_utilization_pct !== undefined 
      ? `${ems.renewable_utilization_pct.toFixed(2)} %` 
      : "unavailable";
  }

  // Battery Throughput
  const batEl = document.getElementById("rep-bat-throughput");
  if (batEl) {
    if (ems.battery_throughput_kwh !== undefined && ems.battery_equivalent_cycles !== undefined) {
      batEl.innerText = `${ems.battery_throughput_kwh.toFixed(2)} kWh (${ems.battery_equivalent_cycles.toFixed(4)} Equivalent Cycles)`;
    } else {
      batEl.innerText = "unavailable";
    }
  }

  // Critical Unmet Demand (Separate from Total Reliability)
  const unmetCritEl = document.getElementById("rep-unmet-critical");
  if (unmetCritEl) {
    if (ems.dispatch_safety && ems.dispatch_safety.critical_unmet_total_wh !== undefined) {
      unmetCritEl.innerText = `${ems.dispatch_safety.critical_unmet_total_wh.toFixed(1)} Wh (Critical Load Only)`;
    } else if (ems.unmet_critical_load_kwh !== undefined) {
      unmetCritEl.innerText = `${(ems.unmet_critical_load_kwh * 1000.0).toFixed(1)} Wh (Critical Load Only)`;
    } else {
      unmetCritEl.innerText = "unavailable / not verified";
    }
  }

  // Total System Reliability
  const relEl = document.getElementById("rep-total-reliability");
  if (relEl) {
    relEl.innerText = ems.system_reliability_pct !== undefined 
      ? `${ems.system_reliability_pct.toFixed(2)} %` 
      : "unavailable";
  }

  // Active Forecast Engine Identity
  const engEl = document.getElementById("rep-engine-identity");
  if (engEl) {
    engEl.innerText = "LocalBaselineForecastEngine (Artifact Fallback — Not N6)";
  }

  // Execution-Run Irradiance MAE
  const maeEl = document.getElementById("rep-execution-mae");
  if (maeEl) {
    maeEl.innerText = solarMetrics.mae !== undefined 
      ? `${solarMetrics.mae.toFixed(4)} W/m² (Evaluated on Replay Trajectory)` 
      : "unavailable";
  }

  const s03MaeEl = document.getElementById("screen03-execution-mae");
  if (s03MaeEl) {
    s03MaeEl.innerText = solarMetrics.mae !== undefined 
      ? `${solarMetrics.mae.toFixed(4)} W/m² (Evaluated on Replay Trajectory)` 
      : "unavailable / not evaluated";
  }

  // Provenance & Winner Status
  const provEl = document.getElementById("rep-provenance");
  if (provEl) {
    provEl.innerText = (govData && govData.data_provenance) || report.data_mode || "OFFLINE_PILOT_ARTIFACT_REPLAY";
  }

  const winEl = document.getElementById("rep-winner-status");
  if (winEl) {
    winEl.innerText = (govData && govData.winner_status !== undefined) ? `${govData.winner_status} (Zero Models Promoted)` : "null (Zero Models Promoted)";
  }
}

// RENDER STATUS & METRICS
function renderStatusReport(report) {
  if (!report || report.error) return;

  const timestampEl = document.getElementById("hmi-timestamp");
  if (timestampEl && report.run_id) {
    timestampEl.innerText = report.run_id.replace("polaris_run_d2_offline_", "");
  }

  const ems = report.ems_evaluation || {};

  // Overview Ribbon
  if (ems.unmet_critical_load_kwh !== undefined) {
    const unmetEl = document.getElementById("overview-unmet");
    if (unmetEl) unmetEl.innerText = `${ems.unmet_critical_load_kwh.toFixed(1)} kWh`;
  }
  if (ems.renewable_utilization_pct !== undefined) {
    const renEl = document.getElementById("overview-ren-pct");
    if (renEl) renEl.innerText = `${ems.renewable_utilization_pct.toFixed(2)} %`;
  }

  // Derive Current Simulator State SOC from authoritative current-state energy (89.6 kWh) and capacity (200 kWh)
  const socEl = document.getElementById("overview-soc");
  const socSubEl = document.getElementById("overview-soc-sub");
  if (socEl) {
    let energyKwh = 89.6;
    let capacityKwh = 200.0;
    if (socSubEl && socSubEl.innerText) {
      const match = socSubEl.innerText.match(/([\d.]+)\s*kWh\s*\/\s*([\d.]+)\s*kWh/);
      if (match) {
        energyKwh = parseFloat(match[1]);
        capacityKwh = parseFloat(match[2]);
      }
    }
    const derivedSocPct = ((energyKwh / capacityKwh) * 100).toFixed(1);
    socEl.innerText = `${derivedSocPct} %`;
  }

  // Optimization Status Panel
  const optStatusEl = document.getElementById("opt-status");
  if (optStatusEl) {
    optStatusEl.innerText = report.execution_status || "SUCCESS_CLEAN";
  }

  // Overview 24h Trend Table Elements
  if (ems.total_diesel_fuel_liters !== undefined) {
    const el = document.getElementById("overview-diesel-fuel");
    if (el) el.innerText = `${ems.total_diesel_fuel_liters.toFixed(2)} Liters`;
  }
  if (ems.total_diesel_energy_kwh !== undefined) {
    const el = document.getElementById("overview-diesel-energy");
    if (el) el.innerText = `${ems.total_diesel_energy_kwh.toFixed(2)} kWh`;
  }
  if (ems.total_renewable_energy_used_kwh !== undefined) {
    const el = document.getElementById("overview-ren-used");
    if (el) el.innerText = `${ems.total_renewable_energy_used_kwh.toFixed(2)} kWh`;
  }
  if (ems.total_renewable_curtailment_kwh !== undefined && ems.renewable_curtailment_pct !== undefined) {
    const el = document.getElementById("overview-ren-curt");
    if (el) el.innerText = `${ems.total_renewable_curtailment_kwh.toFixed(2)} kWh (${ems.renewable_curtailment_pct.toFixed(2)}%)`;
  }
  if (ems.battery_throughput_kwh !== undefined && ems.battery_equivalent_cycles !== undefined) {
    const el = document.getElementById("overview-bat-throughput");
    if (el) el.innerText = `${ems.battery_throughput_kwh.toFixed(2)} kWh (${ems.battery_equivalent_cycles.toFixed(4)} cycles)`;
  }
}

// RENDER FORECAST MATRIX TABLE & SVG TREND
function renderForecastBundle(bundle) {
  if (!bundle || !bundle.timestamps) return;

  const tbody = document.querySelector("#forecast-table tbody");
  if (tbody) {
    tbody.innerHTML = "";
    const timestamps = bundle.timestamps;
    const solarIrr = (bundle.solar_irradiance && bundle.solar_irradiance.point) || [];
    const solarGen = (bundle.solar_generation && bundle.solar_generation.point) || [];
    const windGen = (bundle.wind_generation && bundle.wind_generation.point) || [];
    const demand = (bundle.demand && bundle.demand.point) || [];

    for (let i = 0; i < timestamps.length; i++) {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td class="mono">k = ${i + 1}</td>
        <td class="mono">${timestamps[i]}</td>
        <td class="mono cyan">${(solarIrr[i] || 0).toFixed(2)}</td>
        <td class="mono cyan">${(solarGen[i] || 0).toFixed(1)}</td>
        <td class="mono">${(windGen[i] || 0).toFixed(1)}</td>
        <td class="mono amber">${(demand[i] || 0).toFixed(1)}</td>
      `;
      tbody.appendChild(tr);
    }
  }

  renderForecastTrend(bundle);
}

// RENDER DISPATCH MATRIX TABLE (SOLVES A2 SEMANTIC MAPPING)
function renderDispatchPlan(plan) {
  if (!plan || !plan.timestamps) return;

  const tbody = document.querySelector("#dispatch-table tbody");
  const timestamps = plan.timestamps;
  const solarUsed = plan.solar_used || [];
  const solarCurt = plan.solar_curtailed || [];
  const batChg = plan.battery_charge || [];
  const batDis = plan.battery_discharge || [];
  const dieselPwr = plan.diesel_power || [];
  
  // A2 CORRECTION: Map plan.battery_soc (List[float] in %) from SciPy MILP backend schema
  const socPct = plan.battery_soc || plan.battery_soc_pct || [];

  if (tbody) {
    tbody.innerHTML = "";
    for (let i = 0; i < timestamps.length; i++) {
      const tr = document.createElement("tr");
      if (i === 0) {
        tr.style.backgroundColor = "rgba(6, 182, 212, 0.15)"; // Highlight H1 action
      }
      tr.innerHTML = `
        <td class="mono">${i === 0 ? "H1 EXEC" : "k = " + (i + 1)}</td>
        <td class="mono">${timestamps[i]}</td>
        <td class="mono cyan">${(solarUsed[i] || 0).toFixed(1)}</td>
        <td class="mono amber">${(solarCurt[i] || 0).toFixed(1)}</td>
        <td class="mono green">${(batChg[i] || 0).toFixed(1)}</td>
        <td class="mono green">${(batDis[i] || 0).toFixed(1)}</td>
        <td class="mono amber">${(dieselPwr[i] || 0).toFixed(1)}</td>
        <td class="mono green">${(socPct[i] !== undefined ? socPct[i] : 0).toFixed(1)} %</td>
      `;
      tbody.appendChild(tr);
    }
  }

  // Update dynamic values in Overview / Flow Diagram
  if (solarUsed.length > 0) {
    const solKw = (solarUsed[0] / 1000.0).toFixed(1);
    const solEl = document.getElementById("overview-solar");
    if (solEl) solEl.innerText = `${solKw} kW`;
    const flowSol = document.getElementById("flow-node-solar");
    if (flowSol) flowSol.innerText = `${solKw} kW`;
  }
  if (dieselPwr.length > 0) {
    const diesKw = (dieselPwr[0] / 1000.0).toFixed(1);
    const diesEl = document.getElementById("overview-diesel");
    if (diesEl) diesEl.innerText = `${diesKw} kW`;
    const flowDies = document.getElementById("flow-node-diesel");
    if (flowDies) flowDies.innerText = `${diesKw} kW`;
  }
  if (socPct.length > 0) {
    const socVal = (socPct[0] !== undefined ? socPct[0] : 0).toFixed(1);
    const gaugeBar = document.getElementById("battery-gauge-bar");
    if (gaugeBar) {
      gaugeBar.style.width = `${socVal}%`;
      gaugeBar.innerText = `${socVal}%`;
    }
  }
  const mpcCycleEl = document.getElementById("opt-mpc-cycle");
  if (mpcCycleEl) mpcCycleEl.innerText = "k = 1 / H = 24 (Receding Horizon)";
  if (plan.objective_value !== undefined) {
    const objEl = document.getElementById("opt-objective");
    if (objEl) objEl.innerText = `${plan.objective_value.toFixed(2)}`;
  }
  if (plan.constraint_status) {
    const statusEl = document.getElementById("opt-status");
    if (statusEl) statusEl.innerText = plan.constraint_status;
  }
  if (plan.solve_time_ms !== undefined) {
    const solveEl = document.getElementById("opt-solve-time");
    if (solveEl) solveEl.innerText = `${plan.solve_time_ms.toFixed(1)} ms`;
  }
}

// SVG ENGINEERING TREND VISUALIZATIONS
function renderOverviewTrend(bundle, plan) {
  const container = document.getElementById("overview-trend-svg");
  if (!container || !bundle || !bundle.timestamps) return;

  const demand = (bundle.demand && bundle.demand.point) || [];
  const solarUsed = (plan && plan.solar_used) || [];
  const dieselPwr = (plan && plan.diesel_power) || [];

  const width = container.clientWidth || 550;
  const height = container.clientHeight || 200;
  const pad = { top: 20, right: 20, bottom: 30, left: 45 };

  const maxVal = Math.max(
    ...demand,
    ...solarUsed,
    ...dieselPwr,
    10000
  );

  const pointsCount = bundle.timestamps.length;
  const getX = (i) => pad.left + (i / (pointsCount - 1)) * (width - pad.left - pad.right);
  const getY = (val) => height - pad.bottom - (val / maxVal) * (height - pad.top - pad.bottom);

  let pathDemand = "";
  let pathSolar = "";
  let pathDiesel = "";

  for (let i = 0; i < pointsCount; i++) {
    const x = getX(i);
    const yd = getY(demand[i] || 0);
    const ys = getY(solarUsed[i] || 0);
    const ydi = getY(dieselPwr[i] || 0);

    pathDemand += (i === 0 ? `M ${x} ${yd}` : ` L ${x} ${yd}`);
    pathSolar += (i === 0 ? `M ${x} ${ys}` : ` L ${x} ${ys}`);
    pathDiesel += (i === 0 ? `M ${x} ${ydi}` : ` L ${x} ${ydi}`);
  }

  container.innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" preserveAspectRatio="none">
      <!-- Grid lines -->
      <line x1="${pad.left}" y1="${pad.top}" x2="${width - pad.right}" y2="${pad.top}" stroke="#334155" stroke-dasharray="2,2" />
      <line x1="${pad.left}" y1="${(height - pad.bottom + pad.top)/2}" x2="${width - pad.right}" y2="${(height - pad.bottom + pad.top)/2}" stroke="#334155" stroke-dasharray="2,2" />
      <line x1="${pad.left}" y1="${height - pad.bottom}" x2="${width - pad.right}" y2="${height - pad.bottom}" stroke="#475569" />
      
      <!-- Axis Labels -->
      <text x="${pad.left}" y="${pad.top - 6}" fill="#94A3B8" font-size="9" font-family="monospace">${(maxVal/1000).toFixed(0)} kW</text>
      <text x="${pad.left}" y="${height - pad.bottom + 16}" fill="#94A3B8" font-size="9" font-family="monospace">t+1</text>
      <text x="${width - pad.right - 20}" y="${height - pad.bottom + 16}" fill="#94A3B8" font-size="9" font-family="monospace">t+24</text>

      <!-- Lines -->
      <path d="${pathDemand}" fill="none" stroke="#F59E0B" stroke-width="2" />
      <path d="${pathSolar}" fill="none" stroke="#06B6D4" stroke-width="2" />
      <path d="${pathDiesel}" fill="none" stroke="#EF4444" stroke-width="1.5" stroke-dasharray="3,3" />
    </svg>
  `;
}

function renderForecastTrend(bundle) {
  const container = document.getElementById("forecast-trend-svg");
  if (!container || !bundle || !bundle.timestamps) return;

  const solarIrr = (bundle.solar_irradiance && bundle.solar_irradiance.point) || [];
  const solarGen = (bundle.solar_generation && bundle.solar_generation.point) || [];

  const width = container.clientWidth || 550;
  const height = container.clientHeight || 200;
  const pad = { top: 20, right: 20, bottom: 30, left: 45 };

  const maxIrr = Math.max(...solarIrr, 500);

  const pointsCount = bundle.timestamps.length;
  const getX = (i) => pad.left + (i / (pointsCount - 1)) * (width - pad.left - pad.right);
  const getY = (val) => height - pad.bottom - (val / maxIrr) * (height - pad.top - pad.bottom);

  let pathIrr = "";
  let areaIrr = `M ${getX(0)} ${height - pad.bottom}`;

  for (let i = 0; i < pointsCount; i++) {
    const x = getX(i);
    const y = getY(solarIrr[i] || 0);
    pathIrr += (i === 0 ? `M ${x} ${y}` : ` L ${x} ${y}`);
    areaIrr += ` L ${x} ${y}`;
  }
  areaIrr += ` L ${getX(pointsCount - 1)} ${height - pad.bottom} Z`;

  container.innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" preserveAspectRatio="none">
      <defs>
        <linearGradient id="irrGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#06B6D4" stop-opacity="0.3"/>
          <stop offset="100%" stop-color="#06B6D4" stop-opacity="0.0"/>
        </linearGradient>
      </defs>

      <line x1="${pad.left}" y1="${pad.top}" x2="${width - pad.right}" y2="${pad.top}" stroke="#334155" stroke-dasharray="2,2" />
      <line x1="${pad.left}" y1="${height - pad.bottom}" x2="${width - pad.right}" y2="${height - pad.bottom}" stroke="#475569" />

      <text x="${pad.left}" y="${pad.top - 6}" fill="#94A3B8" font-size="9" font-family="monospace">${maxIrr.toFixed(0)} W/m²</text>
      <text x="${pad.left}" y="${height - pad.bottom + 16}" fill="#94A3B8" font-size="9" font-family="monospace">t+1</text>
      <text x="${width - pad.right - 20}" y="${height - pad.bottom + 16}" fill="#94A3B8" font-size="9" font-family="monospace">t+24</text>

      <path d="${areaIrr}" fill="url(#irrGrad)" />
      <path d="${pathIrr}" fill="none" stroke="#06B6D4" stroke-width="2.5" />
    </svg>
  `;
}

function renderDigitalTwinSOCTrend(plan) {
  const container = document.getElementById("digital-twin-soc-svg");
  if (!container || !plan || !plan.timestamps) return;

  const socPct = plan.battery_soc || plan.battery_soc_pct || [];
  if (socPct.length === 0) return;

  const width = container.clientWidth || 550;
  const height = container.clientHeight || 200;
  const pad = { top: 20, right: 20, bottom: 30, left: 45 };

  const pointsCount = socPct.length;
  const getX = (i) => pad.left + (i / (pointsCount - 1)) * (width - pad.left - pad.right);
  const getY = (val) => height - pad.bottom - (val / 100.0) * (height - pad.top - pad.bottom);

  let pathSoc = "";
  let areaSoc = `M ${getX(0)} ${height - pad.bottom}`;

  for (let i = 0; i < pointsCount; i++) {
    const x = getX(i);
    const y = getY(socPct[i] || 0);
    pathSoc += (i === 0 ? `M ${x} ${y}` : ` L ${x} ${y}`);
    areaSoc += ` L ${x} ${y}`;
  }
  areaSoc += ` L ${getX(pointsCount - 1)} ${height - pad.bottom} Z`;

  container.innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" preserveAspectRatio="none">
      <defs>
        <linearGradient id="socGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#10B981" stop-opacity="0.3"/>
          <stop offset="100%" stop-color="#10B981" stop-opacity="0.0"/>
        </linearGradient>
      </defs>

      <!-- 20% SOC Min Limit & 90% Max Limit reference lines -->
      <line x1="${pad.left}" y1="${getY(90)}" x2="${width - pad.right}" y2="${getY(90)}" stroke="#F59E0B" stroke-dasharray="3,3" />
      <line x1="${pad.left}" y1="${getY(20)}" x2="${width - pad.right}" y2="${getY(20)}" stroke="#EF4444" stroke-dasharray="3,3" />
      <line x1="${pad.left}" y1="${height - pad.bottom}" x2="${width - pad.right}" y2="${height - pad.bottom}" stroke="#475569" />

      <text x="${pad.left}" y="${getY(90) - 4}" fill="#F59E0B" font-size="8" font-family="monospace">SOC REFERENCE (90%)</text>
      <text x="${pad.left}" y="${getY(20) - 4}" fill="#EF4444" font-size="8" font-family="monospace">SOC MIN (20%)</text>
      <text x="${pad.left}" y="${height - pad.bottom + 16}" fill="#94A3B8" font-size="9" font-family="monospace">Step 1</text>
      <text x="${width - pad.right - 25}" y="${height - pad.bottom + 16}" fill="#94A3B8" font-size="9" font-family="monospace">Step 24</text>

      <path d="${areaSoc}" fill="url(#socGrad)" />
      <path d="${pathSoc}" fill="none" stroke="#10B981" stroke-width="2.5" />
    </svg>
  `;
}
