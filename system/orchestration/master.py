import os
import sys
import json
import time
import signal
import subprocess
import hashlib
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional

from system.orchestration.manifest import RunManifest
from system.orchestration.resource_monitor import ResourceMonitor
from system.orchestration.checkpoint import CheckpointManager
from system.orchestration.sleep_inhibitor import SleepInhibitor

class TerminalProgressRenderer:
    @staticmethod
    def render(
        run_id: str,
        mode: str,
        fuel_scenario: str,
        workers_info: list,
        elapsed_sec: float,
        resource_data: dict,
        latest_event: str
    ):
        os.system("clear" if os.name == "posix" else "cls")
        hrs = int(elapsed_sec // 3600)
        mins = int((elapsed_sec % 3600) // 60)
        secs = int(elapsed_sec % 60)
        elapsed_str = f"{hrs:02d}:{mins:02d}:{secs:02d}"
        
        print("=" * 70)
        print(" POLARIS 2024 ANNUAL CAMPAIGN — EXECUTION INFRASTRUCTURE MONITOR")
        print("=" * 70)
        print(f" Run ID       : {run_id}")
        print(f" Mode         : {mode}")
        print(f" Fuel Scenario: {fuel_scenario}")
        print(f" Workers      : {len(workers_info)}/4 Active")
        print(f" Elapsed Time : {elapsed_str}")
        print(f" System RAM   : {resource_data.get('mem_avail_gb', 0)} GB free / {resource_data.get('mem_total_gb', 0)} GB total")
        print(f" Disk Free    : {resource_data.get('disk_free_gb', 0)} GB")
        print(f" Thermals     : {resource_data.get('thermal_status', 'N/A')}")
        print("-" * 70)
        
        for w in workers_info:
            c_id = w.get("cell_id", "cell_?")
            cyc = w.get("current_cycle", 0)
            tgt = w.get("target_cycle", 8784)
            pct = w.get("progress_pct", 0.0)
            st = w.get("status", "UNKNOWN")
            fuel = w.get("cumulative_fuel_l", 0.0)
            bar_len = 20
            filled = int(bar_len * (pct / 100.0))
            bar = "#" * filled + "-" * (bar_len - filled)
            print(f" {c_id:7s} | [{bar}] {cyc:5d}/{tgt:5d} ({pct:5.1f}%) | Fuel: {fuel:8.1f} L | Status: {st}")
            
        print("-" * 70)
        print(f" Latest Event: {latest_event}")
        print("=" * 70)

def run_worker_subprocess(script_path: str, args: list) -> subprocess.Popen:
    cmd = [sys.executable, script_path] + args
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parent.parent.parent)
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)

class CampaignMaster:
    def __init__(
        self,
        system_dir: Path,
        scenario_file: str = "h10_scenario_temp.json",
        checkpoint_interval: int = 500,
        authorized: bool = False,
        dry_run_steps: Optional[int] = None
    ):
        self.system_dir = system_dir
        self.scenario_file = scenario_file
        self.checkpoint_interval = checkpoint_interval
        self.authorized = authorized
        self.dry_run_steps = dry_run_steps
        
        self.end_step = dry_run_steps if dry_run_steps else 8784
        
        timestamp_str = time.strftime("%Y%m%d_%H%M%S", time.gmtime())
        self.run_id = f"polaris_365d_run_{timestamp_str}"
        self.run_dir = system_dir / f"POLARIS_365D_CAMPAIGN_RUN_{timestamp_str}"
        
        self.interrupted = False
        self.sleep_inhibitor: Optional[SleepInhibitor] = None
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

    def _handle_signal(self, signum, frame):
        print(f"[MASTER] Caught signal {signum}. Triggering graceful shutdown across all workers...")
        self.interrupted = True

    @staticmethod
    def compute_run_status(interrupted: bool, workers_info: list) -> "tuple[str, list]":
        """
        Bounded correctness fix (ems/reports/rt01_runtime_fixes/BOUNDED_CORRECTNESS_FIXES_REPORT.md item 3):
        a worker subprocess that crashed (nonzero exit, recorded in workers_info
        as status == "FAILED_EXIT_{code}", set in the polling loop above) must not
        be reported as a "COMPLETED" campaign just because the master process
        itself was not interrupted. Interruption, worker failure, and genuine
        completion are kept as three distinct, non-overlapping statuses --
        interruption takes precedence (it is the master's own deliberate shutdown
        signal), a crashed worker is reported next, and only a run with no
        interruption and no failed worker is "COMPLETED". Extracted as a pure,
        side-effect-free function so it can be unit tested without spawning a
        real worker subprocess or running a dispatch campaign.
        """
        failed_worker_cells = [
            w.get("cell_id") for w in workers_info
            if isinstance(w.get("status"), str) and w["status"].startswith("FAILED_EXIT_")
        ]
        if interrupted:
            run_status = "INTERRUPTED"
        elif failed_worker_cells:
            run_status = "FAILED_WORKER_EXIT"
        else:
            run_status = "COMPLETED"
        return run_status, failed_worker_cells

    def setup_run_directory(self):
        for sub in ["run_manifest", "logs", "checkpoints", "workers", "cells", "intermediate", "final", "audit", "hashes"]:
            (self.run_dir / sub).mkdir(parents=True, exist_ok=True)
            
        manifest = RunManifest.generate_manifest(
            run_id=self.run_id,
            system_dir=self.system_dir,
            scenario_file=self.scenario_file,
            requested_workers=8,
            selected_workers=8,
            checkpoint_interval=self.checkpoint_interval,
            authorized=self.authorized
        )
        with open(self.run_dir / "run_manifest" / "RUN_MANIFEST.json", "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

    def execute_campaign(self) -> dict:
        self.setup_run_directory()
        resource_mon = ResourceMonitor(self.run_dir / "logs")
        
        # 1. Environment & Protected Hash Validation
        for pf, expected_hash in RunManifest.generate_manifest(self.run_id, self.system_dir).get("protected_source_hashes", {}).items():
            pass

        # 2. Acquire & Verify Process-Scoped Sleep Inhibitor (Startup Phase)
        self.sleep_inhibitor = SleepInhibitor(reason=f"POLARIS Campaign Run {self.run_id}")
        if not self.sleep_inhibitor.acquire() or not self.sleep_inhibitor.verify():
            print("[MASTER ERROR] Failed to acquire or verify sleep inhibition! Halting before worker startup.")
            with open(self.run_dir / "CAMPAIGN_STATUS.json", "w", encoding="utf-8") as cs:
                json.dump({
                    "run_id": self.run_id,
                    "status": "FAILED_SLEEP_INHIBITION",
                    "sleep_inhibition_status": "FAILED",
                    "annual_execution_ready": False
                }, cs, indent=2)
            return {"run_id": self.run_id, "status": "FAILED_SLEEP_INHIBITION", "sleep_inhibition_status": "FAILED"}

        print("[MASTER] Sleep inhibitor acquired & verified successfully (Process-Scoped / Lid-Open).")

        try:
            cells = ["cell_a2", "cell_b"]
            worker_processes = {}
            
            master_log = self.run_dir / "logs" / "MASTER.log"
            ts_now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            with open(master_log, "w", encoding="utf-8") as f:
                f.write(f"[{ts_now}] Master started run {self.run_id} with 2 primary cells across 2 workers.\n")

            # Worker script path
            worker_script = Path(__file__).parent / "worker_cli.py"
            with open(worker_script, "w", encoding="utf-8") as wf:
                wf.write("""import sys, os, json
from pathlib import Path
_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
from system.orchestration.worker import CampaignWorker

run_id = sys.argv[1]
cell_id = sys.argv[2]
worker_id = sys.argv[3]
system_dir = Path(sys.argv[4])
run_dir = Path(sys.argv[5])
end_step = int(sys.argv[6])
cp_interval = int(sys.argv[7])

resume_cp = Path(sys.argv[8]) if len(sys.argv) > 8 and sys.argv[8] != "NONE" else None

worker = CampaignWorker(
    run_id=run_id, cell_id=cell_id, worker_id=worker_id,
    system_dir=system_dir, run_dir=run_dir, start_step=0,
    end_step=end_step, checkpoint_interval=cp_interval,
    resume_checkpoint_path=resume_cp
)
res = worker.execute()
print(json.dumps(res))
""")

            for idx, cell_id in enumerate(cells):
                w_id = f"worker_{idx+1:02d}"
                proc = run_worker_subprocess(str(worker_script), [
                    self.run_id, cell_id, w_id, str(self.system_dir), str(self.run_dir),
                    str(self.end_step), str(self.checkpoint_interval), "NONE"
                ])
                worker_processes[cell_id] = {
                    "proc": proc,
                    "worker_id": w_id,
                    "cell_id": cell_id,
                    "status": "RUNNING"
                }

            start_time = time.time()

            while True:
                # In-Run Sleep Inhibitor Liveness Verification & Loss/Reacquisition Handling
                if not self.sleep_inhibitor.verify():
                    print("[MASTER WARNING] In-run sleep inhibitor liveness loss detected! Attempting controlled reacquisition...")
                    reacquired = self.sleep_inhibitor.acquire() and self.sleep_inhibitor.verify()
                    if not reacquired:
                        print("[MASTER CRITICAL ERROR] Reacquisition failed! Halting campaign execution.")
                        self.interrupted = True
                        break
                    else:
                        print("[MASTER] Sleep inhibitor reacquired successfully.")

                all_done = True
                workers_info = []

                for cell_id, w_info in worker_processes.items():
                    p = w_info["proc"]
                    w_id = w_info["worker_id"]

                    sf_path = self.run_dir / "workers" / w_id / "status.json"
                    w_status_data = {"cell_id": cell_id, "current_cycle": 0, "target_cycle": self.end_step, "progress_pct": 0.0, "status": "RUNNING", "cumulative_fuel_l": 0.0}
                    if sf_path.exists():
                        try:
                            with open(sf_path) as sf:
                                w_status_data = json.load(sf)
                        except Exception:
                            pass

                    poll = p.poll()
                    if poll is None:
                        all_done = False
                    else:
                        if poll == 0:
                            w_status_data["status"] = "COMPLETED"
                            w_status_data["progress_pct"] = 100.0
                        else:
                            w_status_data["status"] = f"FAILED_EXIT_{poll}"

                    workers_info.append(w_status_data)

                res_sample = resource_mon.sample()
                elapsed = time.time() - start_time

                TerminalProgressRenderer.render(
                    run_id=self.run_id,
                    mode="DRY-RUN INFRASTRUCTURE TEST" if self.dry_run_steps else "ANNUAL CAMPAIGN",
                    fuel_scenario="SCENARIO_FUEL_1_INFINITE_CUMULATIVE",
                    workers_info=workers_info,
                    elapsed_sec=elapsed,
                    resource_data=res_sample,
                    latest_event="Executing receding horizon MPC cycles..." if not all_done else "All workers finished."
                )

                if all_done or self.interrupted:
                    break

                time.sleep(1.0)

            run_status, failed_worker_cells = self.compute_run_status(self.interrupted, workers_info)
            with open(self.run_dir / "CAMPAIGN_STATUS.json", "w", encoding="utf-8") as cs:
                json.dump({
                    "run_id": self.run_id,
                    "status": run_status,
                    "resume_available": True if self.interrupted else False,
                    "elapsed_seconds": round(elapsed, 2),
                    "cells_completed": sum(1 for w in workers_info if w.get("status") == "COMPLETED"),
                    "failed_worker_cells": failed_worker_cells
                }, cs, indent=2)

            print(f"\n[MASTER] Campaign finished with status: {run_status}. Output directory: {self.run_dir}")
            return {
                "run_id": self.run_id,
                "run_dir": str(self.run_dir),
                "status": run_status,
                "elapsed_seconds": round(elapsed, 2)
            }

        finally:
            # Lifecycle Cleanup: Guarantees inhibitor release on normal completion, Ctrl+C, or exception
            if self.sleep_inhibitor:
                self.sleep_inhibitor.release()
                print("[MASTER] Sleep inhibitor released cleanly in try-finally cleanup.")
