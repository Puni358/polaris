import sys, os, json
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
