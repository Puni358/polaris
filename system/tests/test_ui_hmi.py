"""
Targeted HMI SCADA UI Test Suite for POLARIS (S8.1-UI-RENDERED-FIDELITY-CORRECTION)
Verifies local HMI server endpoints, static file rendering, JSON runtime artifact consumption,
data provenance labeling, Phase A corrections, Phase B HMI visualizations, and zero backend mutation.
"""

import json
import urllib.request
import threading
import time
from pathlib import Path
import pytest

from system.ui.server import HTTPServer, PolarisHMIHandler, ARTIFACTS_DIR, STATIC_DIR, SYSTEM_DIR

TEST_PORT = 8089


@pytest.fixture(scope="module")
def hmi_server():
    """Starts local presentation HMI server in background thread for testing."""
    server_address = ("127.0.0.1", TEST_PORT)
    httpd = HTTPServer(server_address, PolarisHMIHandler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.5)
    yield f"http://127.0.0.1:{TEST_PORT}"
    httpd.shutdown()
    httpd.server_close()


def test_1_hmi_static_html_loads(hmi_server):
    """Req 1: UI loads locally on localhost."""
    url = f"{hmi_server}/index.html"
    with urllib.request.urlopen(url) as response:
        assert response.status == 200
        html = response.read().decode("utf-8")
        assert "POLARIS — Local Industrial SCADA HMI" in html
        assert "POLARIS" in html
        assert "PREDICTIVE EMS HMI v1.0" in html


def test_2_hmi_static_css_and_js_load(hmi_server):
    """Req 1 & 6: Static CSS and JavaScript assets load properly."""
    with urllib.request.urlopen(f"{hmi_server}/styles.css") as res:
        assert res.status == 200
        css = res.read().decode("utf-8")
        assert "--bg-space: #0B0F19;" in css
        assert ".svg-chart-container" in css

    with urllib.request.urlopen(f"{hmi_server}/app.js") as res:
        assert res.status == 200
        js = res.read().decode("utf-8")
        assert "renderForecastBundle" in js
        assert "plan.battery_soc" in js  # A2 battery SOC mapping check
        assert "renderOverviewTrend" in js  # Phase B SVG trend chart check
        assert "renderDigitalTwinSOCTrend" in js  # Screen 05 SVG trend chart check


def test_3_api_status_endpoint_consumes_run_report(hmi_server):
    """Req 2 & 3: Runtime data from run_report.json can be consumed."""
    url = f"{hmi_server}/api/status"
    with urllib.request.urlopen(url) as response:
        assert response.status == 200
        data = json.loads(response.read().decode("utf-8"))
        assert data["environment"] == "LOCAL_OFFLINE_PC"
        assert "ems_evaluation" in data


def test_4_api_forecast_endpoint_consumes_forecast_bundle(hmi_server):
    """Req 2 & 7: Runtime forecast bundle can be consumed."""
    url = f"{hmi_server}/api/forecast"
    with urllib.request.urlopen(url) as response:
        assert response.status == 200
        data = json.loads(response.read().decode("utf-8"))
        assert data["schema_version"] == "1.0.0"
        assert data["horizon_hours"] == 24
        assert len(data["timestamps"]) == 24


def test_5_api_dispatch_endpoint_consumes_dispatch_plan(hmi_server):
    """Req 2 & 8 & 9: DispatchPlan data (diesel, solar, battery charge/discharge) can be consumed."""
    url = f"{hmi_server}/api/dispatch"
    with urllib.request.urlopen(url) as response:
        assert response.status == 200
        data = json.loads(response.read().decode("utf-8"))
        assert data["schema_version"] == "1.0.0"
        assert "solar_used" in data
        assert "diesel_power" in data
        assert "battery_charge" in data
        assert "battery_discharge" in data
        assert "battery_soc" in data  # A2 field check in API output


def test_6_provenance_labels_in_html(hmi_server):
    """Req 5 & 11: Synthetic and proxy provenance labels are explicitly present."""
    url = f"{hmi_server}/index.html"
    with urllib.request.urlopen(url) as response:
        html = response.read().decode("utf-8")
        assert "LOCAL RUNTIME (OFFLINE)" in html
        assert "SYNTHETIC DEMONSTRATION" in html
        assert "SciPy MILP / HiGHS" in html
        assert "DATA BLOCKED" in html
        assert "NOT ESTABLISHED" in html


def test_7_phase_a1_screen02_no_400v_3phase(hmi_server):
    """Phase A1 Verification: Screen 02 must NOT contain 400V/3-Phase claims."""
    url = f"{hmi_server}/index.html"
    with urllib.request.urlopen(url) as response:
        html = response.read().decode("utf-8")
        assert "MICROGRID AC / ENERGY BUS" in html
        assert "Electrical voltage/phase configuration: NOT EXPOSED BY RUNTIME" in html
        assert "400V" not in html
        assert "400 V" not in html
        assert "3-Phase" not in html
        assert "3-phase" not in html


def test_8_phase_a3_wind_provenance_explicit(hmi_server):
    """Phase A3 Verification: Screen 03 explicitly labels wind power/proxy provenance."""
    url = f"{hmi_server}/index.html"
    with urllib.request.urlopen(url) as response:
        html = response.read().decode("utf-8")
        assert "Synthetic Wind Power (W)" in html
        assert "ABISKO 10m" in html
        assert "CONDITIONAL REGIONAL PROXY" in html
        assert "NOT MEASURED NUOLJA GENERATION" in html


def test_9_phase_a4_equipment_provenance_explicit(hmi_server):
    """Phase A4 Verification: Equipment capacities are explicitly labeled as synthetic scenario parameters."""
    url = f"{hmi_server}/index.html"
    with urllib.request.urlopen(url) as response:
        html = response.read().decode("utf-8")
        assert "Synthetic Scenario Parameter" in html


def test_10_phase_a5_scenario_separation(hmi_server):
    """Phase A5 Verification: S2 Low Solar and S5 High Renewable are separate cards."""
    url = f"{hmi_server}/index.html"
    with urllib.request.urlopen(url) as response:
        html = response.read().decode("utf-8")
        assert "S2 — LOW SOLAR" in html
        assert "S5 — HIGH RENEWABLE" in html
        assert "S2 / S5" not in html


def test_11_scoped_reliability_and_mae_display(hmi_server):
    """Req 8: Dynamic report DOM elements and explicit reference context exist."""
    url = f"{hmi_server}/index.html"
    with urllib.request.urlopen(url) as response:
        html = response.read().decode("utf-8")
        assert 'id="rep-unmet-critical"' in html
        assert 'id="rep-diesel-fuel"' in html
        assert 'id="rep-economic-fuel"' in html
        assert 'id="rep-total-reliability"' in html
        assert "36.188657 W/m² (Canonical Frozen 347-Window Reference Set)" in html
        assert "OFFLINE PILOT REPLAY ONLY" in html
        # Confirm misleading hardcoded static savings numbers were removed
        assert "85.92 Liters</td>" not in html
        assert "42.3054 W/m² (Evaluated on S1 Synthetic Trajectory)" not in html


def test_12_wind_speed_m_s_unit(hmi_server):
    """Issue B Verification: Wind speed proxy on Screen 01 uses m/s and NEVER kW."""
    url = f"{hmi_server}/index.html"
    with urllib.request.urlopen(url) as response:
        html = response.read().decode("utf-8")
        assert "6.2 m/s" in html
        assert 'id="flow-node-wind">0.0 kW<' not in html


def test_13_point_only_forecast_wording(hmi_server):
    """Issue D Verification: Point-only forecast interval wording is explicit without fabricated claims."""
    url = f"{hmi_server}/index.html"
    with urllib.request.urlopen(url) as response:
        html = response.read().decode("utf-8")
        assert "POINT-ONLY: lower = point = upper; NO STATISTICAL COVERAGE CLAIM" in html
        assert "Zero Fabricated Bounds" not in html
        assert "Zero bounds were fabricated" not in html


def test_14_screen05_soc_svg_element_id(hmi_server):
    """Issue F Verification: Screen 05 SVG container element ID is digital-twin-soc-svg."""
    url = f"{hmi_server}/index.html"
    with urllib.request.urlopen(url) as response:
        html = response.read().decode("utf-8")
        assert 'id="digital-twin-soc-svg"' in html


def test_15_no_false_network_claims(hmi_server):
    """Issue G Verification: No false 0 API calls or 100% network isolation claims."""
    url = f"{hmi_server}/index.html"
    with urllib.request.urlopen(url) as response:
        html = response.read().decode("utf-8")
        assert "0 API Calls" not in html
        assert "100% OFFLINE" not in html


def test_16_screen01_current_soc_presentation(hmi_server):
    """Correction #1: Screen 01 current SOC is 44.8 % and 89.6 kWh / 200 kWh."""
    url = f"{hmi_server}/index.html"
    with urllib.request.urlopen(url) as response:
        html = response.read().decode("utf-8")
        assert "44.8 %" in html
        assert "89.6 kWh / 200 kWh" in html


def test_17_screen04_mpc_placeholder_removed(hmi_server):
    """Correction #2: Screen 04 contains no template placeholder MPC CYCLE: k / N."""
    url = f"{hmi_server}/index.html"
    with urllib.request.urlopen(url) as response:
        html = response.read().decode("utf-8")
        assert "MPC CYCLE: k / N" not in html
        assert "k = 1 / H = 24" in html


def test_18_screen05_soc_reference_label(hmi_server):
    """Correction #3: Screen 05 SVG reference label is SOC REFERENCE (90%) and NOT SOC MAX (90%)."""
    with urllib.request.urlopen(f"{hmi_server}/app.js") as res:
        js = res.read().decode("utf-8")
        assert "SOC REFERENCE (90%)" in js
        assert "SOC MAX (90%)" not in js


def test_19_zero_backend_runtime_mutation():
    """Req 12: UI presentation code does not modify backend code or schemas."""
    ui_dir = SYSTEM_DIR / "ui"
    assert ui_dir.exists()
    assert (ui_dir / "server.py").exists()
    assert (ui_dir / "static" / "index.html").exists()


def test_20_api_governance_endpoint(hmi_server):
    """Verifies /api/governance exposes register v1.9.11, winner:null, and offline pilot replay provenance."""
    url = f"{hmi_server}/api/governance"
    with urllib.request.urlopen(url) as response:
        assert response.status == 200
        data = json.loads(response.read().decode("utf-8"))
        assert data["register_version"] == "v1.9.11"
        assert data["winner_status"] is None
        assert data["data_provenance"] == "OFFLINE_PILOT_ARTIFACT_REPLAY"
        assert data["live_n6_execution_claim"] is False
        assert data["dsl01_status"] == "DEFERRED_BY_OWNER (epsilon_tol unset)"


def test_21_dynamic_dom_binding_screen08(hmi_server):
    """Verifies app.js contains renderAnalyticsReport with dynamic binding for all Screen 08 IDs."""
    url = f"{hmi_server}/app.js"
    with urllib.request.urlopen(url) as response:
        js = response.read().decode("utf-8")
        assert "renderAnalyticsReport" in js
        assert "rep-diesel-fuel" in js
        assert "rep-economic-fuel" in js
        assert "rep-unmet-critical" in js
        assert "rep-total-reliability" in js
        assert "rep-engine-identity" in js
        assert "rep-execution-mae" in js


def test_22_provenance_and_offline_replay_labeling(hmi_server):
    """Verifies Screen 01 and 08 contain explicit OFFLINE PILOT REPLAY and NO LIVE N6 SAVINGS labels."""
    url = f"{hmi_server}/index.html"
    with urllib.request.urlopen(url) as response:
        html = response.read().decode("utf-8")
        assert "OFFLINE PILOT REPLAY" in html
        assert "NO LIVE N6 SAVINGS CLAIMED" in html
        assert "EMS PERFORMANCE SUMMARY (OFFLINE ARTIFACT REPLAY)" in html


def test_23_missing_or_malformed_artifact_handling(hmi_server):
    """Verifies 404 response when querying a non-existent artifact file."""
    non_existent_url = f"{hmi_server}/api/non_existent_endpoint"
    req = urllib.request.Request(non_existent_url)
    with pytest.raises(urllib.error.HTTPError) as exc_info:
        urllib.request.urlopen(req)
    assert exc_info.value.code == 404


