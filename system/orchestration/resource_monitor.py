import os, sys, shutil, time, csv, subprocess, platform
from pathlib import Path
from typing import Dict, Any

class ResourceMonitor:
    def __init__(self, log_dir: Path):
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.csv_path = log_dir / "RESOURCE_MONITOR.csv"
        
        # Check sleep inhibition binary
        self.sleep_inhibit_bin = shutil.which("systemd-inhibit") or shutil.which("gnome-session-inhibit")
        self.sleep_inhibition_status = "ACTIVE" if self.sleep_inhibit_bin else "UNAVAILABLE"
        
        self._init_csv()

    def _init_csv(self):
        if not self.csv_path.exists():
            with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "timestamp", "cpu_count", "mem_total_gb", "mem_avail_gb", 
                    "disk_free_gb", "thermal_status", "sleep_inhibition_status"
                ])

    def sample(self) -> Dict[str, Any]:
        mem_total_gb = 0.0
        mem_avail_gb = 0.0
        if os.path.exists("/proc/meminfo"):
            with open("/proc/meminfo") as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        mem_total_gb = int(line.split()[1]) / (1024**2)
                    elif line.startswith("MemAvailable:"):
                        mem_avail_gb = int(line.split()[1]) / (1024**2)
                        
        disk_free_gb = shutil.disk_usage(".").free / (1024**3)
        
        thermal_zones = {}
        if os.path.exists("/sys/class/thermal"):
            for z in os.listdir("/sys/class/thermal"):
                if z.startswith("thermal_zone"):
                    tf = os.path.join("/sys/class/thermal", z, "temp")
                    ty = os.path.join("/sys/class/thermal", z, "type")
                    if os.path.exists(tf):
                        try:
                            val = int(open(tf).read().strip()) / 1000.0
                            ztype = open(ty).read().strip() if os.path.exists(ty) else z
                            thermal_zones[ztype] = val
                        except Exception:
                            pass
                            
        thermal_str = str(thermal_zones) if thermal_zones else "THERMAL_TELEMETRY=UNAVAILABLE"
        
        sample_data = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "cpu_count": os.cpu_count(),
            "mem_total_gb": round(mem_total_gb, 2),
            "mem_avail_gb": round(mem_avail_gb, 2),
            "disk_free_gb": round(disk_free_gb, 2),
            "thermal_status": thermal_str,
            "sleep_inhibition_status": self.sleep_inhibition_status
        }
        
        with open(self.csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                sample_data["timestamp"], sample_data["cpu_count"], sample_data["mem_total_gb"],
                sample_data["mem_avail_gb"], sample_data["disk_free_gb"],
                sample_data["thermal_status"], sample_data["sleep_inhibition_status"]
            ])
            
        return sample_data
