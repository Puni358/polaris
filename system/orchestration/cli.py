import sys, os
from pathlib import Path
_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
import sys, argparse
from pathlib import Path
from system.orchestration.master import CampaignMaster
from system.orchestration.aggregator import CampaignAggregator

def main():
    # Pre-process positional subcommands if passed (e.g. run-annual-campaign)
    if len(sys.argv) > 1 and sys.argv[1] == "run-annual-campaign":
        sys.argv.pop(1)

    parser = argparse.ArgumentParser(description="POLARIS 2024 Annual Campaign Orchestrator CLI")
    parser.add_argument("--year", type=int, default=2024, help="Target calendar year")
    parser.add_argument("--workers", type=int, default=8, help="Number of parallel worker processes (default: 8)")
    parser.add_argument("--checkpoint-interval", type=int, default=500, help="Checkpoint interval in steps")
    parser.add_argument("--sleep-inhibit", action="store_true", default=True, help="Enable Ubuntu process-scoped sleep inhibition")
    parser.add_argument("--output-dir", type=str, default=None, help="Custom output directory path")
    parser.add_argument("--dry-run", action="store_true", help="Run 48-step dry-run infrastructure test")
    parser.add_argument("--execute-authorized", action="store_true", help="Execute annual campaign (requires explicit human authorization)")
    parser.add_argument("--resume", type=str, help="Resume an interrupted campaign run ID")
    parser.add_argument("--verify", type=str, help="Verify and aggregate completed run ID")
    
    args = parser.parse_args()
    system_dir = Path(__file__).parent.parent
    
    if args.dry_run:
        print("[CLI] Starting 48-step Dry-Run Infrastructure Test across 2 primary cells (Cell A & Cell B)...")
        master = CampaignMaster(system_dir=system_dir, dry_run_steps=48, authorized=False, checkpoint_interval=args.checkpoint_interval)
        res = master.execute_campaign()
        print(f"[CLI] Dry-run finished. Aggregating results...")
        agg = CampaignAggregator.aggregate_results(Path(res["run_dir"]), expected_cycles=48)
        print("[CLI] Aggregation SUCCESS! Primary 2-Cell Summary:")
        import json
        print(json.dumps(agg["primary_2cell_comparison"], indent=2))
    elif args.execute_authorized:
        print("[CLI] Starting 2024 8,784-hour Annual POLARIS Campaign across 2 primary cells (Cell A & Cell B)...")
        master = CampaignMaster(system_dir=system_dir, dry_run_steps=None, authorized=True, checkpoint_interval=args.checkpoint_interval)
        res = master.execute_campaign()
        print(f"[CLI] Annual campaign execution completed. Aggregating results...")
        agg = CampaignAggregator.aggregate_results(Path(res["run_dir"]), expected_cycles=8784)
        print("[CLI] Aggregation SUCCESS! Primary 2-Cell Summary:")
        import json
        print(json.dumps(agg["primary_2cell_comparison"], indent=2))
    elif args.verify:
        run_path = Path(args.verify)
        agg = CampaignAggregator.aggregate_results(run_path)
        import json
        print(json.dumps(agg, indent=2))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
