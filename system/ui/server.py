"""
POLARIS Local HMI SCADA Presentation Server
Lightweight offline HTTP presentation server for POLARIS local HMI dashboard.
Reads authoritative runtime artifacts and serves static control room interface on localhost.
"""

import sys
import json
import argparse
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Dict, Any

SYSTEM_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = SYSTEM_DIR.parent
STATIC_DIR = Path(__file__).resolve().parent / "static"
ARTIFACTS_DIR = SYSTEM_DIR / "artifacts"

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from system.runtime.runner import PolarisLocalRunner


class PolarisHMIHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def do_GET(self):
        # Route API endpoints to authoritative POLARIS runtime output artifacts
        if self.path == "/api/status":
            self._send_json_file(ARTIFACTS_DIR / "run_report.json")
        elif self.path == "/api/forecast":
            self._send_json_file(ARTIFACTS_DIR / "latest_forecast_bundle.json")
        elif self.path == "/api/dispatch":
            self._send_json_file(ARTIFACTS_DIR / "latest_dispatch_plan.json")
        elif self.path == "/api/comparison":
            self._send_json_file(ARTIFACTS_DIR / "demo_comparison_report.json")
        elif self.path == "/api/scenarios":
            self._send_json_file(ARTIFACTS_DIR / "multi_scenario_evaluation_report.json")
        elif self.path == "/api/governance":
            gov_data = {
                "schema_version": "1.0.0",
                "register_version": "v1.9.11",
                "date": "2026-10-19",
                "winner_status": None,
                "active_model_promotion": "NONE",
                "rt01_status": "resolved_with_evidence",
                "dsl01_status": "DEFERRED_BY_OWNER (epsilon_tol unset)",
                "data_provenance": "OFFLINE_PILOT_ARTIFACT_REPLAY",
                "live_n6_execution_claim": False,
                "disclaimer": "DIGITAL TWIN / PILOT ARTIFACT REPLAY ONLY — Not verified N6 operational performance or production deployment."
            }
            self._send_json_data(gov_data)
        else:
            # Fall back to static files (index.html, styles.css, app.js)
            super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/run"):
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
            try:
                params = json.loads(body)
            except Exception:
                params = {}

            scenario = params.get("scenario", "demo_scenario.json")
            steps = int(params.get("steps", 24))
            engine = params.get("forecast_engine", "stage81_solar")
            optimizer = params.get("optimizer", "milp")

            runner = PolarisLocalRunner(
                SYSTEM_DIR,
                scenario_filename=scenario,
                optimizer_type=optimizer,
                forecast_engine_type=engine
            )
            report = runner.run_pipeline(steps_to_run=steps)
            self._send_json_data(report)
        else:
            self.send_error(404, "Endpoint not found")

    def _send_json_file(self, file_path: Path):
        if not file_path.exists():
            self._send_json_data({"error": f"Artifact {file_path.name} not found. Run POLARIS pipeline first."}, status=404)
            return
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._send_json_data(data)
        except Exception as e:
            self._send_json_data({"error": str(e)}, status=500)

    def _send_json_data(self, data: Dict[str, Any], status: int = 200):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        # Silently log requests or print clean HMI status
        sys.stderr.write(f"[POLARIS HMI SERVER] {format % args}\n")


def start_server(port: int = 8080):
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    server_address = ("127.0.0.1", port)
    httpd = HTTPServer(server_address, PolarisHMIHandler)
    print("==================================================")
    print(f"POLARIS LOCAL INDUSTRIAL SCADA HMI SERVER")
    print("==================================================")
    print(f"Environment:     LOCAL RUNTIME (100% OFFLINE)")
    print(f"Display Surface: http://localhost:{port}")
    print(f"Host Address:    127.0.0.1:{port}")
    print(f"Artifacts Dir:   {ARTIFACTS_DIR}")
    print("Press Ctrl+C to terminate local server.")
    print("==================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nPOLARIS HMI server stopped cleanly.")
        httpd.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="POLARIS Local HMI Server")
    parser.add_argument("--port", type=int, default=8080, help="Port to run localhost HMI server")
    args = parser.parse_args()
    start_server(args.port)
