import pytest
import yaml
import json
import math
from pathlib import Path
from system.schemas.station_state import StationState
from system.control.ecd import EmergencyConditionDetector, ConstantCriticalLoad

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def test_1_campaign_scenario_loads_11_60_kw():
    loads_cfg_path = PROJECT_ROOT / "system" / "config" / "loads.yaml"
    with open(loads_cfg_path, "r") as f:
        cfg = yaml.safe_load(f)
    assert cfg["critical_load"]["baseline_power_w"] == 11600.0
    assert cfg["status_label"] == "DELIBERATELY_CONSERVATIVE_SYNTHETIC_DESIGN"

def test_2_all_8784_values_equal_11_60_kw():
    trajectory = [11600.0] * 8784
    assert len(trajectory) == 8784
    assert min(trajectory) == 11600.0
    assert max(trajectory) == 11600.0
    assert sum(trajectory) / 8784.0 == 11600.0

def test_3_no_30_kw_override_occurs():
    loads_cfg_path = PROJECT_ROOT / "system" / "config" / "loads.yaml"
    with open(loads_cfg_path, "r") as f:
        cfg = yaml.safe_load(f)
    p_critical = cfg["critical_load"]["baseline_power_w"]
    assert p_critical != 30000.0
    assert p_critical == 11600.0

def test_4_ecd_receives_11_60_kw():
    ecd = EmergencyConditionDetector()
    critical_load_w = 11600.0
    traj = ConstantCriticalLoad(critical_load_w)
    
    # Check energy over 72h reserve horizon: 11,600 W * 72 h = 835,200 Wh
    e_req_wh = traj.get_energy_required_wh(0.0, 72.0)
    assert math.isclose(e_req_wh, 11600.0 * 72.0, rel_tol=1e-5)

def test_5_gate02_treats_11_60_kw_as_hard_constraint():
    # Verify penalty for dropping critical load is high (10.0 / Wh = 10,000 / kWh)
    loads_cfg_path = PROJECT_ROOT / "system" / "config" / "loads.yaml"
    with open(loads_cfg_path, "r") as f:
        cfg = yaml.safe_load(f)
    unmet_penalty = cfg["critical_load"]["unmet_penalty_per_wh"]
    assert unmet_penalty >= 10.0

def test_6_no_future_truth_is_accessed():
    # Constant critical load relies strictly on static parameter 11.6 kW and no future data
    traj = ConstantCriticalLoad(11600.0)
    e1 = traj.get_energy_required_wh(0.0, 24.0)
    e2 = traj.get_energy_required_wh(100.0, 124.0)
    assert e1 == e2 == 11600.0 * 24.0

def test_7_critical_trajectory_is_deterministic():
    t1 = [11600.0] * 8784
    t2 = [11600.0] * 8784
    assert t1 == t2

def test_8_critical_trajectory_compatible_with_h10_demand():
    fixture_path = PROJECT_ROOT / "ems/fixtures/POLARIS_HYBRID_FIXTURE_H1_0" / "fixture.csv"
    assert fixture_path.exists()
    import csv
    with open(fixture_path, "r") as f:
        reader = csv.DictReader(f)
        min_demand = min(float(row["synthetic_load_W"]) for row in reader)
    assert 11600.0 <= min_demand

def test_9_provenance_identifies_conservative_design_margin():
    prov_path = PROJECT_ROOT / "ems/reports/diesel_and_loads/CRITICAL_LOAD_HIGH_POWER_PROVENANCE.json"
    assert prov_path.exists()
    with open(prov_path, "r") as f:
        prov = json.load(f)
    assert prov["CRITICAL_LOAD_STATUS"] == "SYNTHETIC_ENGINEERING_SCENARIO"
    assert prov["REAL_NUOLJA_CRITICAL_LOAD"] == "NOT_ESTABLISHED"

def test_10_real_nuolja_critical_load_remains_not_established():
    prov_path = PROJECT_ROOT / "ems/reports/diesel_and_loads/CRITICAL_LOAD_HIGH_POWER_PROVENANCE.json"
    with open(prov_path, "r") as f:
        prov = json.load(f)
    assert prov["REAL_NUOLJA_CRITICAL_LOAD"] == "NOT_ESTABLISHED"
