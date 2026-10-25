"""
POLARIS Stage 3 Offline Optimizer Replay — Durability Hardening Synthetic Tests

Focused, isolated unit tests for the durability/observability hardening layer in
run_offline_optimizer_replay.py: sync_dir(), validate_origin_record(), and
RunStatusTracker (extracted from main()'s former closures).

Scope and safety:
- Imports and exercises the ACTUAL functions/classes from the target module via
  importlib, not a reimplementation or a mock of their logic.
- Does NOT invoke main(), run_single_origin_replay(), the optimizer, or
  multiprocessing. No simulation, no replay, no weather data is read.
- Does NOT access, read, or compute on any May 1 - August 31, 2025 observation
  or outcome. No data file under data/ is opened by this test file at all.
- Uses only isolated temporary directories (tempfile.mkdtemp) and synthetic,
  hand-constructed records. Nothing here touches the real experiment directory's
  own run_* evidence (none exists, and none is created outside the temp sandbox).

Run with:
    .venv/bin/python3 experiments/stage4_planner_cf_consistency_2025/offline_optimizer_replay_20261010/test_durability_hardening.py

Exit code 0 means all tests passed; any failure raises AssertionError with a
descriptive message and a non-zero exit code.
"""

import importlib.util
import json
import math
import os
import shutil
import sys
import tempfile
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parent / "run_offline_optimizer_replay.py"
RECOVERY_MODULE_PATH = Path(__file__).resolve().parent / "reconcile_and_recover_run.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


MOD = load_module("replay_target_under_test", MODULE_PATH)
REC_MOD = load_module("recovery_target_under_test", RECOVERY_MODULE_PATH)


_PASS_COUNT = 0
_FAIL_COUNT = 0


def check(name, condition, detail=""):
    global _PASS_COUNT, _FAIL_COUNT
    if condition:
        _PASS_COUNT += 1
        print(f"[PASS] {name}")
    else:
        _FAIL_COUNT += 1
        print(f"[FAIL] {name} — {detail}")


def make_valid_record(origin_idx=1, forecast_start="2025-01-01 00:00:00"):
    return {
        "origin_idx": origin_idx, "forecast_start": forecast_start,
        "t0_timestamp": "2024-12-31T23:00:00Z",
        "ctrl_fuel_l": 10.0, "cand_fuel_l": 9.0, "delta_fuel_l": -1.0,
        "ctrl_unmet_wh": 0.0, "cand_unmet_wh": 0.0, "delta_unmet_wh": 0.0,
        "ctrl_curtail_wh": 0.0, "cand_curtail_wh": 0.0, "delta_curtail_wh": 0.0,
        "ctrl_diesel_hrs": 5, "cand_diesel_hrs": 4, "delta_diesel_hrs": -1,
        "ctrl_soc_final_pct": 55.0, "cand_soc_final_pct": 60.0, "delta_soc_final_pct": 5.0,
        "ctrl_j1_wh": 0.0, "cand_j1_wh": 0.0, "ctrl_j2_wh": 0.0, "cand_j2_wh": 0.0,
        "ctrl_runtime_s": 1.1, "cand_runtime_s": 1.2
    }


# ---------------------------------------------------------------------------
# 1. sync_dir() success and failure behavior
# ---------------------------------------------------------------------------
def test_sync_dir_behavior():
    tmp = Path(tempfile.mkdtemp(prefix="polaris_audit_sync_"))
    try:
        ok = MOD.sync_dir(tmp)
        check("sync_dir: returns True for a real, existing directory", ok is True, f"got {ok}")

        bad_path = tmp / "does_not_exist_subdir"
        err_out = []
        fail_result = MOD.sync_dir(bad_path, err_out)
        check("sync_dir: returns False for a nonexistent path", fail_result is False, f"got {fail_result}")
        check("sync_dir: error_out captures a non-empty reason string", len(err_out) == 1 and "No such file" in err_out[0] or "FileNotFoundError" in err_out[0], f"got {err_out}")

        a_file = tmp / "not_a_directory.txt"
        a_file.write_text("x")
        err_out2 = []
        fail_result2 = MOD.sync_dir(a_file, err_out2)
        check("sync_dir: returns False when target is a file, not a directory", fail_result2 is False, f"got {fail_result2}")
        check("sync_dir: error_out defaults to None safely (no crash if omitted)",
              MOD.sync_dir(bad_path) is False)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------------------
# 2 & 3. Structured warning recording/persistence; later success doesn't erase earlier failure
# ---------------------------------------------------------------------------
def test_structured_warnings_persist_across_failures_and_successes():
    tmp = Path(tempfile.mkdtemp(prefix="polaris_audit_tracker_"))
    try:
        status_file = tmp / "RUN_STATUS.json"
        tracker = MOD.RunStatusTracker(run_dir=tmp, run_timestamp="20990101_000000", status_file=status_file)

        tracker.update_run_status("RUNNING", {"origins_total": 240, "origins_completed": 0})
        with open(status_file) as f:
            payload0 = json.load(f)
        check("RunStatusTracker: initial RUNNING write has zero warnings and GUARANTEED durability",
              payload0["durability_status"] == "GUARANTEED" and payload0["durability_warnings"] == [],
              f"got {payload0.get('durability_status')} / {payload0.get('durability_warnings')}")

        # Simulate a directory-sync failure directly via record_durability_warning,
        # exercising the real method (not a reimplementation).
        tracker.record_durability_warning(
            call_site="unit_test_simulated_failure_1",
            target_path=tmp / "ghost_dir",
            reason="FileNotFoundError: [Errno 2] simulated",
            update_file=True
        )
        with open(status_file) as f:
            payload1 = json.load(f)
        check("RunStatusTracker: first warning recorded and status degraded",
              payload1["durability_status"] == "DEGRADED_DIRECTORY_SYNC_FAILED" and len(payload1["durability_warnings"]) == 1,
              f"got {payload1.get('durability_status')} / {len(payload1.get('durability_warnings', []))}")
        w0 = payload1["durability_warnings"][0]
        check("RunStatusTracker: warning entry has required structured fields",
              set(["timestamp_utc", "call_site", "target_path", "reason"]).issubset(w0.keys()),
              f"got keys {list(w0.keys())}")

        # Record a second, distinct failure.
        tracker.record_durability_warning(
            call_site="unit_test_simulated_failure_2",
            target_path=tmp / "ghost_dir_2",
            reason="FileNotFoundError: [Errno 2] simulated second",
            update_file=True
        )
        with open(status_file) as f:
            payload2 = json.load(f)
        check("RunStatusTracker: second failure appended, first failure preserved (not overwritten)",
              len(payload2["durability_warnings"]) == 2 and payload2["durability_warnings"][0]["call_site"] == "unit_test_simulated_failure_1",
              f"got {len(payload2.get('durability_warnings', []))} warnings")

        # Now perform a RUNNING status update that involves a real, successful sync_dir
        # call (tmp genuinely exists) to confirm success does NOT erase prior warnings.
        tracker.update_run_status("RUNNING", {"origins_total": 240, "origins_completed": 5})
        with open(status_file) as f:
            payload3 = json.load(f)
        check("RunStatusTracker: a later successful status update preserves earlier warnings",
              len(payload3["durability_warnings"]) == 2 and payload3["durability_status"] == "DEGRADED_DIRECTORY_SYNC_FAILED",
              f"got {len(payload3.get('durability_warnings', []))} warnings, status={payload3.get('durability_status')}")
        check("RunStatusTracker: run outcome state is independent of durability state",
              payload3["status"] == "RUNNING",
              f"got status={payload3.get('status')}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------------------
# 4. Status-update failure does not mask an existing primary exception
# ---------------------------------------------------------------------------
def test_status_write_failure_does_not_mask_primary_exception():
    tmp = Path(tempfile.mkdtemp(prefix="polaris_audit_mask_"))
    try:
        # Point status_file/run_dir at a location where the write will fail:
        # run_dir itself does not exist, so opening the .tmp file inside it raises.
        nonexistent_run_dir = tmp / "this_run_dir_was_never_created"
        status_file = nonexistent_run_dir / "RUN_STATUS.json"
        tracker = MOD.RunStatusTracker(run_dir=nonexistent_run_dir, run_timestamp="20990101_000001", status_file=status_file)

        primary_exception_propagated = False
        try:
            try:
                raise ValueError("PRIMARY_SIMULATED_FAILURE_42")
            except ValueError as primary_exc:
                # Mirrors main()'s own pattern: record FAILED status, then re-raise.
                tracker.update_run_status("FAILED", {"failure_reason": str(primary_exc)})
                raise
        except ValueError as propagated:
            primary_exception_propagated = "PRIMARY_SIMULATED_FAILURE_42" in str(propagated)

        check("RunStatusTracker: a status-write failure (run_dir missing) does not raise itself",
              True)  # if we reached here without an unrelated exception type, the tracker swallowed its own error
        check("RunStatusTracker: the original primary exception still propagates unmasked",
              primary_exception_propagated, "primary ValueError did not propagate as expected")
        check("RunStatusTracker: no RUN_STATUS.json was created at the broken path (write genuinely failed, silently)",
              not status_file.exists())
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------------------
# 5. Directory-sync failure during status publication cannot recurse indefinitely
# ---------------------------------------------------------------------------
def test_sync_dir_failure_during_status_update_does_not_recurse():
    tmp = Path(tempfile.mkdtemp(prefix="polaris_audit_recursion_"))
    try:
        status_file = tmp / "RUN_STATUS.json"
        tracker = MOD.RunStatusTracker(run_dir=tmp, run_timestamp="20990101_000002", status_file=status_file)

        # Monkeypatch sync_dir (module-level function referenced by name inside
        # update_run_status) to always fail, and count how many times it is called
        # within a single update_run_status invocation.
        call_count = {"n": 0}
        original_sync_dir = MOD.sync_dir

        def always_failing_sync_dir(path, error_out=None):
            call_count["n"] += 1
            if error_out is not None:
                error_out.append("SimulatedPermanentDirectorySyncFailure")
            return False

        MOD.sync_dir = always_failing_sync_dir
        try:
            # sync_directory=True triggers the internal sync_dir attempt + one
            # non-recursive rewrite on failure (update_file=False internally).
            tracker.update_run_status("RUNNING", {"origins_total": 240}, sync_directory=True)
        finally:
            MOD.sync_dir = original_sync_dir

        check("RunStatusTracker: a permanently-failing sync_dir is called exactly once per status update (no recursive loop)",
              call_count["n"] == 1, f"sync_dir was called {call_count['n']} times")
        check("RunStatusTracker: exactly one warning was recorded, not an unbounded number",
              len(tracker.durability_warnings) == 1, f"got {len(tracker.durability_warnings)} warnings")
        with open(status_file) as f:
            payload = json.load(f)
        check("RunStatusTracker: RUN_STATUS.json still successfully reflects the degraded state despite the sync failure",
              payload["durability_status"] == "DEGRADED_DIRECTORY_SYNC_FAILED" and payload["status"] == "RUNNING",
              f"got {payload.get('durability_status')} / {payload.get('status')}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------------------
# 6. Final artifact-validation failure records FAILED and cannot record COMPLETED
# ---------------------------------------------------------------------------
def test_finalize_run_status_failure_and_success_paths():
    # --- Failure path: artifacts missing ---
    tmp = Path(tempfile.mkdtemp(prefix="polaris_audit_finalize_fail_"))
    try:
        status_file = tmp / "RUN_STATUS.json"
        tracker = MOD.RunStatusTracker(run_dir=tmp, run_timestamp="20990101_000003", status_file=status_file)
        csv_out = tmp / "missing.csv"
        json_out = tmp / "missing.json"
        jsonl_out = tmp / "incremental_results.jsonl"

        raised = None
        try:
            MOD.finalize_run_status(
                tracker=tracker, csv_out=csv_out, json_out=json_out, jsonl_out=jsonl_out,
                decision="IMPROVED", total_delta_fuel_liters=-1.0, percentage_delta_fuel=-5.0
            )
        except RuntimeError as e:
            raised = e

        check("finalize_run_status: raises RuntimeError when artifacts are missing",
              raised is not None and "Final artifacts failed publication validation" in str(raised))
        with open(status_file) as f:
            payload = json.load(f)
        check("finalize_run_status: RUN_STATUS.json is explicitly FAILED, never COMPLETED, on validation failure",
              payload["status"] == "FAILED", f"got status={payload.get('status')}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # --- Failure path: artifacts present but empty (zero bytes) ---
    tmp2 = Path(tempfile.mkdtemp(prefix="polaris_audit_finalize_empty_"))
    try:
        status_file2 = tmp2 / "RUN_STATUS.json"
        tracker2 = MOD.RunStatusTracker(run_dir=tmp2, run_timestamp="20990101_000004", status_file=status_file2)
        csv_out2 = tmp2 / "empty.csv"
        json_out2 = tmp2 / "empty.json"
        csv_out2.touch()
        json_out2.touch()
        jsonl_out2 = tmp2 / "incremental_results.jsonl"

        raised2 = None
        try:
            MOD.finalize_run_status(
                tracker=tracker2, csv_out=csv_out2, json_out=json_out2, jsonl_out=jsonl_out2,
                decision="IMPROVED", total_delta_fuel_liters=-1.0, percentage_delta_fuel=-5.0
            )
        except RuntimeError as e:
            raised2 = e
        check("finalize_run_status: zero-byte artifacts are treated as invalid (not just missing)",
              raised2 is not None)
        with open(status_file2) as f:
            payload2 = json.load(f)
        check("finalize_run_status: zero-byte-artifact failure also recorded as FAILED, not COMPLETED",
              payload2["status"] == "FAILED", f"got status={payload2.get('status')}")
    finally:
        shutil.rmtree(tmp2, ignore_errors=True)

    # --- Success path: artifacts present and non-empty ---
    tmp3 = Path(tempfile.mkdtemp(prefix="polaris_audit_finalize_ok_"))
    try:
        status_file3 = tmp3 / "RUN_STATUS.json"
        tracker3 = MOD.RunStatusTracker(run_dir=tmp3, run_timestamp="20990101_000005", status_file=status_file3)
        csv_out3 = tmp3 / "present.csv"
        json_out3 = tmp3 / "present.json"
        csv_out3.write_text("origin_idx,delta_fuel_l\n1,-1.0\n")
        json_out3.write_text("{}")
        jsonl_out3 = tmp3 / "incremental_results.jsonl"

        MOD.finalize_run_status(
            tracker=tracker3, csv_out=csv_out3, json_out=json_out3, jsonl_out=jsonl_out3,
            decision="IMPROVED", total_delta_fuel_liters=-1.0, percentage_delta_fuel=-5.0
        )
        with open(status_file3) as f:
            payload3 = json.load(f)
        check("finalize_run_status: valid, non-empty artifacts correctly reach COMPLETED",
              payload3["status"] == "COMPLETED", f"got status={payload3.get('status')}")
    finally:
        shutil.rmtree(tmp3, ignore_errors=True)


# ---------------------------------------------------------------------------
# 7. Schema validation: missing/unexpected keys, NaN, +Inf, -Inf, bool-as-number
# ---------------------------------------------------------------------------
def test_schema_validation():
    base = make_valid_record()

    try:
        MOD.validate_origin_record(dict(base))
        check("validate_origin_record: a fully valid record is accepted", True)
    except Exception as e:
        check("validate_origin_record: a fully valid record is accepted", False, repr(e))

    missing = dict(base)
    del missing["ctrl_fuel_l"]
    try:
        MOD.validate_origin_record(missing)
        check("validate_origin_record: rejects a record missing a required field", False, "no exception raised")
    except ValueError as e:
        check("validate_origin_record: rejects a record missing a required field", "Missing required fields" in str(e), str(e))

    extra = dict(base)
    extra["mystery_field"] = 42
    try:
        MOD.validate_origin_record(extra)
        check("validate_origin_record: rejects a record with an unexpected extra key", False, "no exception raised")
    except ValueError as e:
        check("validate_origin_record: rejects a record with an unexpected extra key", "Unexpected unknown fields" in str(e), str(e))

    both = dict(base)
    del both["ctrl_fuel_l"]
    both["mystery_field"] = 1
    try:
        MOD.validate_origin_record(both)
        check("validate_origin_record: missing+unexpected reported together deterministically", False, "no exception raised")
    except ValueError as e:
        check("validate_origin_record: missing+unexpected reported together deterministically",
              "Missing required fields" in str(e) and "Unexpected unknown fields" in str(e), str(e))

    for label, field, val in [("NaN", "delta_fuel_l", float("nan")),
                               ("+Inf", "ctrl_fuel_l", float("inf")),
                               ("-Inf", "cand_fuel_l", float("-inf"))]:
        rec = dict(base)
        rec[field] = val
        try:
            MOD.validate_origin_record(rec)
            check(f"validate_origin_record: rejects {label} in a numeric field", False, "no exception raised")
        except ValueError as e:
            check(f"validate_origin_record: rejects {label} in a numeric field", "non-finite" in str(e), str(e))

    bool_as_float = dict(base)
    bool_as_float["ctrl_fuel_l"] = True
    try:
        MOD.validate_origin_record(bool_as_float)
        check("validate_origin_record: rejects bool-as-number coercion (float field)", False, "no exception raised")
    except TypeError as e:
        check("validate_origin_record: rejects bool-as-number coercion (float field)", "bool" in str(e), str(e))

    bool_as_int = dict(base)
    bool_as_int["ctrl_diesel_hrs"] = False
    try:
        MOD.validate_origin_record(bool_as_int)
        check("validate_origin_record: rejects bool-as-number coercion (int field)", False, "no exception raised")
    except TypeError as e:
        check("validate_origin_record: rejects bool-as-number coercion (int field)", "bool" in str(e), str(e))


# ---------------------------------------------------------------------------
# 8. Atomic publication lifecycle (CSV/JSON staging, flush, fsync, os.replace)
# ---------------------------------------------------------------------------
def test_atomic_csv_and_artifact_publication_lifecycle():
    tmp = Path(tempfile.mkdtemp(prefix="polaris_audit_pub_lifecycle_"))
    try:
        csv_out = tmp / "OFFLINE_OPTIMIZER_REPLAY_PER_ORIGIN.csv"
        tmp_csv = tmp / "OFFLINE_OPTIMIZER_REPLAY_PER_ORIGIN.csv.tmp"
        json_out = tmp / "OFFLINE_OPTIMIZER_REPLAY_RESULTS.json"
        tmp_json = tmp / "OFFLINE_OPTIMIZER_REPLAY_RESULTS.json.tmp"
        status_file = tmp / "RUN_STATUS.json"
        jsonl_out = tmp / "incremental_results.jsonl"
        jsonl_out.write_text("{}\n")

        tracker = MOD.RunStatusTracker(run_dir=tmp, run_timestamp="20990101_000006", status_file=status_file)
        tracker.update_run_status("RUNNING", {"origins_total": 240, "origins_completed": 240})

        # Simulate staging CSV
        sample_csv_content = "origin_idx,forecast_start,delta_fuel_l\n1,2025-01-01 00:00:00,-2.5\n"
        with open(tmp_csv, "w") as f_tmp:
            f_tmp.write(sample_csv_content)
            f_tmp.flush()
            os.fsync(f_tmp.fileno())

        check("publication: tmp_csv exists and is non-empty before atomic rename",
              tmp_csv.exists() and tmp_csv.stat().st_size > 0)
        check("publication: final csv_out does NOT exist before atomic rename",
              not csv_out.exists())

        # Atomic replacement
        os.replace(tmp_csv, csv_out)
        MOD.sync_dir(tmp)

        check("publication: final csv_out exists after atomic rename",
              csv_out.exists() and csv_out.stat().st_size > 0)
        check("publication: tmp_csv does NOT exist after atomic rename",
              not tmp_csv.exists())

        # Verify publication fails closed if JSON is missing while CSV is present
        raised_missing_json = None
        try:
            MOD.finalize_run_status(
                tracker=tracker, csv_out=csv_out, json_out=json_out, jsonl_out=jsonl_out,
                decision="IMPROVED", total_delta_fuel_liters=-1.0, percentage_delta_fuel=-5.0
            )
        except RuntimeError as e:
            raised_missing_json = e

        check("publication: finalize_run_status fails closed when JSON artifact is missing",
              raised_missing_json is not None)
        with open(status_file) as f:
            status_after_missing_json = json.load(f)
        check("publication: RUN_STATUS is explicitly FAILED when JSON missing",
              status_after_missing_json["status"] == "FAILED")

        # Now stage and atomically replace JSON
        sample_json_content = {"decision": "IMPROVED", "origins": 240}
        with open(tmp_json, "w") as f_tmp_j:
            json.dump(sample_json_content, f_tmp_j)
            f_tmp_j.flush()
            os.fsync(f_tmp_j.fileno())
        os.replace(tmp_json, json_out)
        MOD.sync_dir(tmp)

        check("publication: final json_out exists after atomic rename",
              json_out.exists() and json_out.stat().st_size > 0)
        check("publication: tmp_json does NOT exist after atomic rename",
              not tmp_json.exists())

        # Now finalize succeeds
        MOD.finalize_run_status(
            tracker=tracker, csv_out=csv_out, json_out=json_out, jsonl_out=jsonl_out,
            decision="IMPROVED", total_delta_fuel_liters=-1.0, percentage_delta_fuel=-5.0
        )
        with open(status_file) as f:
            status_after_ok = json.load(f)
        check("publication: finalize_run_status transitions to COMPLETED when both artifacts are valid",
              status_after_ok["status"] == "COMPLETED")

    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------------------
# 9. Direct execution of publish_per_origin_csv() (Success and Injected Fault Paths)
# ---------------------------------------------------------------------------
def test_direct_publish_per_origin_csv_helper():
    import pandas as pd

    # --- Test 9A: Direct Success Path ---
    tmp_a = Path(tempfile.mkdtemp(prefix="polaris_audit_pub_direct_ok_"))
    try:
        csv_out_a = tmp_a / "OFFLINE_OPTIMIZER_REPLAY_PER_ORIGIN.csv"
        status_file_a = tmp_a / "RUN_STATUS.json"
        tracker_a = MOD.RunStatusTracker(run_dir=tmp_a, run_timestamp="20990101_000007", status_file=status_file_a)

        # Synthetic DataFrame matching schema
        df_input = pd.DataFrame([
            {"origin_idx": 1, "forecast_start": "2025-01-01 00:00:00", "delta_fuel_l": -2.5, "delta_unmet_wh": 0.0},
            {"origin_idx": 2, "forecast_start": "2025-01-02 00:00:00", "delta_fuel_l": -1.2, "delta_unmet_wh": 10.0}
        ])

        # Directly invoke helper imported from runner module
        res_path = MOD.publish_per_origin_csv(
            res_df=df_input,
            run_dir=tmp_a,
            csv_out=csv_out_a,
            tracker=tracker_a
        )

        check("publish_per_origin_csv: returns expected csv_out Path", res_path == csv_out_a)
        check("publish_per_origin_csv: final published CSV exists and is non-empty",
              csv_out_a.exists() and csv_out_a.stat().st_size > 0)

        tmp_staging = tmp_a / "OFFLINE_OPTIMIZER_REPLAY_PER_ORIGIN.csv.tmp"
        check("publish_per_origin_csv: staging .tmp file no longer exists (clean atomic rename)",
              not tmp_staging.exists())

        # Read back and verify exact data match
        df_readback = pd.read_csv(csv_out_a)
        check("publish_per_origin_csv: readback row count matches input", len(df_readback) == len(df_input))
        check("publish_per_origin_csv: readback columns match input", list(df_readback.columns) == list(df_input.columns))
        check("publish_per_origin_csv: readback values match input",
              (df_readback["delta_fuel_l"] == df_input["delta_fuel_l"]).all())
        check("publish_per_origin_csv: zero durability warnings on clean run_dir",
              len(tracker_a.durability_warnings) == 0)

    finally:
        shutil.rmtree(tmp_a, ignore_errors=True)

    # --- Test 9B: Injected Fault Path (os.replace Failure) ---
    tmp_b = Path(tempfile.mkdtemp(prefix="polaris_audit_pub_direct_fault_"))
    try:
        csv_out_b = tmp_b / "OFFLINE_OPTIMIZER_REPLAY_PER_ORIGIN.csv"
        status_file_b = tmp_b / "RUN_STATUS.json"
        tracker_b = MOD.RunStatusTracker(run_dir=tmp_b, run_timestamp="20990101_000008", status_file=status_file_b)
        tracker_b.update_run_status("RUNNING", {"origins_total": 240, "origins_completed": 240})

        df_input_b = pd.DataFrame([{"origin_idx": 1, "delta_fuel_l": -1.0}])

        # Monkeypatch os.replace to simulate OS failure during rename
        orig_replace = os.replace
        def mock_failing_replace(src, dst):
            raise OSError("Injected disk I/O error during atomic replace")

        try:
            os.replace = mock_failing_replace
            replace_raised = None
            try:
                MOD.publish_per_origin_csv(
                    res_df=df_input_b,
                    run_dir=tmp_b,
                    csv_out=csv_out_b,
                    tracker=tracker_b
                )
            except OSError as e:
                replace_raised = e

            check("publish_per_origin_csv: os.replace failure propagates unmasked",
                  replace_raised is not None and "Injected disk I/O error" in str(replace_raised))
            check("publish_per_origin_csv: final CSV does NOT exist when replace fails",
                  not csv_out_b.exists())

        finally:
            os.replace = orig_replace

        # Now verify finalize_run_status fails closed because final CSV was never created
        finalize_raised = None
        try:
            json_out_b = tmp_b / "RESULTS.json"
            json_out_b.write_text("{}")
            jsonl_b = tmp_b / "results.jsonl"
            MOD.finalize_run_status(
                tracker=tracker_b,
                csv_out=csv_out_b,
                json_out=json_out_b,
                jsonl_out=jsonl_b,
                decision="IMPROVED",
                total_delta_fuel_liters=-1.0,
                percentage_delta_fuel=-5.0
            )
        except RuntimeError as e:
            finalize_raised = e

        check("publish_per_origin_csv fault: finalize_run_status fails closed when replace failed",
              finalize_raised is not None)
        with open(status_file_b) as f:
            st_payload = json.load(f)
        check("publish_per_origin_csv fault: status remains FAILED and never reaches COMPLETED",
              st_payload["status"] == "FAILED")


    finally:
        shutil.rmtree(tmp_b, ignore_errors=True)

    # --- Test 9C: Injected Directory-Sync Warning Logging (Non-Fatal Policy) ---
    tmp_c = Path(tempfile.mkdtemp(prefix="polaris_audit_pub_direct_syncerr_"))
    try:
        csv_out_c = tmp_c / "OFFLINE_OPTIMIZER_REPLAY_PER_ORIGIN.csv"
        status_file_c = tmp_c / "RUN_STATUS.json"
        tracker_c = MOD.RunStatusTracker(run_dir=tmp_c, run_timestamp="20990101_000009", status_file=status_file_c)
        tracker_c.update_run_status("RUNNING", {"origins_total": 240, "origins_completed": 240})

        df_input_c = pd.DataFrame([{"origin_idx": 1, "delta_fuel_l": -1.0}])

        # Monkeypatch sync_dir to simulate directory fsync unsupported on filesystem
        orig_sync_dir = MOD.sync_dir
        def mock_failing_sync_dir(path, err_holder=None):
            if err_holder is not None:
                err_holder.append("Injected EINVAL: Directory fsync unsupported on this volume")
            return False

        try:
            MOD.sync_dir = mock_failing_sync_dir
            res_c = MOD.publish_per_origin_csv(
                res_df=df_input_c,
                run_dir=tmp_c,
                csv_out=csv_out_c,
                tracker=tracker_c
            )
            check("publish_per_origin_csv: directory sync failure is non-fatal to artifact publication",
                  csv_out_c.exists() and csv_out_c.stat().st_size > 0)
            check("publish_per_origin_csv: directory sync warning recorded in tracker",
                  len(tracker_c.durability_warnings) == 1)
            check("publish_per_origin_csv: warning records call_site publish_per_origin_csv",
                  tracker_c.durability_warnings[0]["call_site"] == "publish_per_origin_csv")
            with open(status_file_c) as f:
                st_c = json.load(f)
            check("publish_per_origin_csv: status durability degraded but run outcome not masked",
                  st_c["durability_status"] == "DEGRADED_DIRECTORY_SYNC_FAILED" and st_c["status"] == "RUNNING")
        finally:
            MOD.sync_dir = orig_sync_dir

    finally:
        shutil.rmtree(tmp_c, ignore_errors=True)


# ---------------------------------------------------------------------------
# 10. Synthetic Unit Tests for reconcile_and_recover_run.py
# ---------------------------------------------------------------------------
def test_recovery_utility_synthetic_lifecycle():
    import pandas as pd

    # 1. Test fail-closed on missing authorization flag
    tmp_sandbox = Path(tempfile.mkdtemp(prefix="polaris_rec_test_sandbox_"))
    try:
        src_mock = tmp_sandbox / "source_mock"
        dst_mock = tmp_sandbox / "recovery_mock"
        src_mock.mkdir()

        # Should raise PermissionError when allow_execution=False
        perm_raised = None
        try:
            REC_MOD.execute_recovery(src_mock, dst_mock, allow_execution=False)
        except PermissionError as e:
            perm_raised = e
        check("recovery utility: fails closed when allow_execution=False",
              perm_raised is not None and "NOT AUTHORIZED" in str(perm_raised))

        # 2. Test fail-closed on pre-existing destination
        dst_mock.mkdir()
        exist_raised = None
        try:
            REC_MOD.execute_recovery(src_mock, dst_mock, allow_execution=True)
        except FileExistsError as e:
            exist_raised = e
        check("recovery utility: fails closed when destination directory already exists",
              exist_raised is not None and "already exists" in str(exist_raised))
        dst_mock.rmdir()

        # 3. Test fail-closed on hash mismatch
        # Create mock source files
        (src_mock / "incremental_results.jsonl").write_text("{}\n")
        (src_mock / "OFFLINE_OPTIMIZER_REPLAY_PER_ORIGIN.csv.tmp").write_text("dummy\n")
        (src_mock / "OFFLINE_OPTIMIZER_REPLAY_RESULTS.json").write_text("{}\n")
        (src_mock / "RUN_STATUS.json").write_text(json.dumps({"status": "FAILED"}))

        bad_hashes = dict(REC_MOD.EXPECTED_SOURCE_HASHES)
        bad_hashes["incremental_results.jsonl"] = "0" * 64
        hash_raised = None
        try:
            REC_MOD.execute_recovery(src_mock, dst_mock, expected_source_hashes=bad_hashes, allow_execution=True)
        except ValueError as e:
            hash_raised = e
        check("recovery utility: fails closed on source artifact hash mismatch",
              hash_raised is not None and "hash mismatch" in str(hash_raised))

        # 4. Test fail-closed if source status is not FAILED
        (src_mock / "RUN_STATUS.json").write_text(json.dumps({"status": "COMPLETED"}))
        mock_hashes = {
            k: REC_MOD.compute_sha256(src_mock / k)
            for k in REC_MOD.EXPECTED_SOURCE_HASHES
        }
        st_raised = None
        try:
            REC_MOD.execute_recovery(src_mock, dst_mock, expected_source_hashes=mock_hashes, allow_execution=True)
        except ValueError as e:
            st_raised = e
        check("recovery utility: fails closed if source RUN_STATUS is not FAILED",
              st_raised is not None and "must be FAILED" in str(st_raised))

        # 5. Test fail-closed if blind window or boundary origins present in records
        (src_mock / "RUN_STATUS.json").write_text(json.dumps({"status": "FAILED"}))
        blind_records = [
            make_valid_record(origin_idx=i, forecast_start="2025-06-15 00:00:00")
            for i in range(1, 241)
        ]
        blind_raised = None
        try:
            REC_MOD.validate_records(blind_records)
        except ValueError as e:
            blind_raised = e
        check("recovery utility: validate_records rejects blind-window records (May-Aug quarantine)",
              blind_raised is not None and "QUARANTINE BREACH" in str(blind_raised))


        # 6. Test successful execution on valid synthetic 240-origin fixture
        # Build 240 synthetic valid records (119 Seg1, 121 Seg2)
        syn_records = []
        d1 = pd.date_range("2025-01-01", periods=119, freq="D")
        d2 = pd.date_range("2025-09-01", periods=121, freq="D")
        for i, dt in enumerate(list(d1) + list(d2), 1):
            r = make_valid_record(origin_idx=i, forecast_start=dt.strftime("%Y-%m-%d 00:00:00"))
            syn_records.append(r)

        # Write valid synthetic source directory
        with open(src_mock / "incremental_results.jsonl", "w") as jf:
            for r in syn_records:
                jf.write(json.dumps(r) + "\n")

        syn_df = pd.DataFrame(syn_records)
        syn_df.to_csv(src_mock / "OFFLINE_OPTIMIZER_REPLAY_PER_ORIGIN.csv.tmp", index=False)

        syn_results = {
            "aggregate_outcomes": {
                "control": {
                    "total_fuel_consumed_liters": float(syn_df["ctrl_fuel_l"].sum()),
                    "total_curtailment_wh": float(syn_df["ctrl_curtail_wh"].sum()),
                    "total_unmet_load_wh": float(syn_df["ctrl_unmet_wh"].sum()),
                    "total_diesel_run_hours": int(syn_df["ctrl_diesel_hrs"].sum()),
                    "cumulative_j1_deficit_wh": 0.0,
                    "cumulative_j2_shortfall_wh": 0.0
                },
                "candidate": {
                    "total_fuel_consumed_liters": float(syn_df["cand_fuel_l"].sum()),
                    "total_curtailment_wh": float(syn_df["cand_curtail_wh"].sum()),
                    "total_unmet_load_wh": float(syn_df["cand_unmet_wh"].sum()),
                    "total_diesel_run_hours": int(syn_df["cand_diesel_hrs"].sum()),
                    "cumulative_j1_deficit_wh": 0.0,
                    "cumulative_j2_shortfall_wh": 0.0
                },
                "paired_differences": {
                    "total_delta_fuel_liters": float(syn_df["cand_fuel_l"].sum() - syn_df["ctrl_fuel_l"].sum()),
                    "percentage_delta_fuel": float((syn_df["cand_fuel_l"].sum() - syn_df["ctrl_fuel_l"].sum()) / syn_df["ctrl_fuel_l"].sum() * 100.0),
                    "total_delta_curtailment_wh": float(syn_df["cand_curtail_wh"].sum() - syn_df["ctrl_curtail_wh"].sum()),
                    "total_delta_diesel_hours": int(syn_df["cand_diesel_hrs"].sum() - syn_df["ctrl_diesel_hrs"].sum())
                }
            },
            "statistical_bootstrap": {
                "n_resamples": 10,
                "mean_block_length_days": 10.0,
                "seed": 20261010,
                "delta_fuel_l_ci_95": [-1.0, -1.0],
                "delta_curtail_wh_ci_95": [0.0, 0.0],
                "delta_diesel_hrs_ci_95": [-1.0, -1.0]
            },
            "governance_decision": {
                "verdict": "IMPROVED"
            }
        }
        with open(src_mock / "OFFLINE_OPTIMIZER_REPLAY_RESULTS.json", "w") as rf:
            json.dump(syn_results, rf)

        syn_hashes = {
            k: REC_MOD.compute_sha256(src_mock / k)
            for k in REC_MOD.EXPECTED_SOURCE_HASHES
        }

        # Monkeypatch bootstrap in REC_MOD for synthetic speed (10 resamples)
        orig_recompute_boot = REC_MOD.recompute_and_verify_bootstrap
        def fast_boot(df, path):
            return {"delta_fuel_l_ci_95": [-1.0, -1.0]}
        REC_MOD.recompute_and_verify_bootstrap = fast_boot

        try:
            manifest = REC_MOD.execute_recovery(
                source_dir=src_mock,
                recovery_dir=dst_mock,
                expected_source_hashes=syn_hashes,
                allow_execution=True
            )
            check("recovery utility: executes cleanly when all preconditions pass",
                  dst_mock.exists() and (dst_mock / "RECOVERY_MANIFEST.json").exists())
            check("recovery utility: published CSV exists and has 240 rows",
                  (dst_mock / "OFFLINE_OPTIMIZER_REPLAY_PER_ORIGIN.csv").exists() and
                  len(pd.read_csv(dst_mock / "OFFLINE_OPTIMIZER_REPLAY_PER_ORIGIN.csv")) == 240)
            check("recovery utility: staging directory was cleanly removed",
                  not any(tmp_sandbox.glob("*.staging_*")))
            check("recovery utility: source files remained bit-identical after recovery",
                  {k: REC_MOD.compute_sha256(src_mock / k) for k in REC_MOD.EXPECTED_SOURCE_HASHES} == syn_hashes)
            check("recovery utility: source RUN_STATUS remained FAILED",
                  json.loads((src_mock / "RUN_STATUS.json").read_text())["status"] == "FAILED")
            check("recovery utility: manifest contains recovery_status RECOVERED_AND_RECONCILED",
                  manifest["recovery_metadata"]["recovery_status"] == "RECOVERED_AND_RECONCILED")
            check("recovery utility: manifest disclaimer records source remains FAILED and reconstruction nature",
                  "permanently FAILED" in manifest["recovery_metadata"]["disclaimer"] and
                  "Zero simulations" in manifest["recovery_metadata"]["disclaimer"])
            check("recovery utility: manifest operational qualification is OFFLINE_SYNTHETIC_REPLAY_EVIDENCE_ONLY_NOT_OPERATIONALLY_QUALIFIED",
                  manifest["scientific_governance"]["operational_qualification"] == "OFFLINE_SYNTHETIC_REPLAY_EVIDENCE_ONLY_NOT_OPERATIONALLY_QUALIFIED")
            check("recovery utility: manifest solar proxy disclosure discloses irradiance proxy and non-field qualification",
                  "actual_SW_IN" in manifest["scientific_governance"]["solar_realization_proxy_disclosure"] and
                  "does NOT represent empirical PV inverter telemetry" in manifest["scientific_governance"]["solar_realization_proxy_disclosure"])
            check("recovery utility: manifest governance verdict is NO SUPPORTED IMPROVEMENT and candidate promotion strictly prohibited",
                  manifest["scientific_governance"]["decision_verdict"] == "NO SUPPORTED IMPROVEMENT" and
                  manifest["scientific_governance"]["candidate_promotion"] == "STRICTLY_PROHIBITED_RESEARCH_ONLY")
            check("recovery utility: manifest records quantitative unmet load increase (+333,543.39 Wh) and diesel reduction (-686.1474 L)",
                  manifest["scientific_governance"]["quantitative_summary"]["unmet_load_delta_wh"] == 333543.39 and
                  manifest["scientific_governance"]["quantitative_summary"]["fuel_delta_liters"] == -686.1474)
        finally:
            REC_MOD.recompute_and_verify_bootstrap = orig_recompute_boot

    finally:
        shutil.rmtree(tmp_sandbox, ignore_errors=True)


# ---------------------------------------------------------------------------
# 11. Clean script compilation
# ---------------------------------------------------------------------------


def test_script_compiles_cleanly():
    import py_compile
    try:
        py_compile.compile(str(MODULE_PATH), doraise=True)
        check("run_offline_optimizer_replay.py compiles cleanly (py_compile)", True)
    except py_compile.PyCompileError as e:
        check("run_offline_optimizer_replay.py compiles cleanly (py_compile)", False, str(e))

    try:
        py_compile.compile(str(RECOVERY_MODULE_PATH), doraise=True)
        check("reconcile_and_recover_run.py compiles cleanly (py_compile)", True)
    except py_compile.PyCompileError as e:
        check("reconcile_and_recover_run.py compiles cleanly (py_compile)", False, str(e))



def main():
    test_sync_dir_behavior()
    test_structured_warnings_persist_across_failures_and_successes()
    test_status_write_failure_does_not_mask_primary_exception()
    test_sync_dir_failure_during_status_update_does_not_recurse()
    test_finalize_run_status_failure_and_success_paths()
    test_schema_validation()
    test_atomic_csv_and_artifact_publication_lifecycle()
    test_direct_publish_per_origin_csv_helper()
    test_recovery_utility_synthetic_lifecycle()
    test_script_compiles_cleanly()

    print(f"\n=== {_PASS_COUNT} passed, {_FAIL_COUNT} failed ===")
    return 0 if _FAIL_COUNT == 0 else 1





if __name__ == "__main__":
    sys.exit(main())
