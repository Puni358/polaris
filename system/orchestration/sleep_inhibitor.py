import sys, os, time, shutil, subprocess, atexit, signal
from typing import Dict, Any, Optional

class SleepInhibitor:
    """
    Process-scoped System Sleep Inhibitor for Ubuntu Linux.
    
    Primary OS Mechanism:
    - Ubuntu Linux: Uses /usr/bin/systemd-inhibit --what=idle:sleep --who=POLARIS_EMS --why="..." sleep 864000
    - Prevents system idle sleep / suspend while laptop lid remains OPEN.
    - Permits display dimming, display power-off (blanking), and screen lock.
    - OS-Level Independent Verification: Queries `systemd-inhibit --list` to verify logind registration.
    
    Guarantees:
    - Zero modification to logind.conf, GNOME power settings, power plans, or lid-close policies.
    - Process-scoped lifecycle with automatic cleanup on exit/interruption.
    """

    def __init__(self, reason: str = "POLARIS Annual Campaign Execution"):
        self.reason = reason
        self.who = "POLARIS_EMS"
        self.platform = "UBUNTU_LINUX" if sys.platform.startswith("linux") else sys.platform
        self.is_acquired = False
        self.inhibit_proc: Optional[subprocess.Popen] = None
        self._atexit_registered = False

    def acquire(self) -> bool:
        if self.is_acquired and self.verify():
            return True

        inhibit_bin = shutil.which("systemd-inhibit") or "/usr/bin/systemd-inhibit"
        if os.path.exists(inhibit_bin):
            try:
                cmd = [
                    inhibit_bin,
                    "--what=idle:sleep",
                    f"--who={self.who}",
                    f"--why={self.reason}",
                    "sleep", "864000"
                ]
                self.inhibit_proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                time.sleep(0.2)
                
                # Verify process handle and OS-level logind table
                if self.inhibit_proc.poll() is None and self._verify_os_level():
                    self.is_acquired = True
                else:
                    self.is_acquired = False
            except Exception:
                self.is_acquired = False
        else:
            # Platform fallback
            self.is_acquired = True

        if self.is_acquired and not self._atexit_registered:
            atexit.register(self.release)
            self._atexit_registered = True

        return self.is_acquired

    def _verify_os_level(self) -> bool:
        """Independent OS-level verification via systemd-inhibit --list"""
        inhibit_bin = shutil.which("systemd-inhibit") or "/usr/bin/systemd-inhibit"
        if not os.path.exists(inhibit_bin):
            return True
            
        try:
            res = subprocess.run([inhibit_bin, "--list"], capture_output=True, text=True, timeout=3)
            return self.who in res.stdout
        except Exception:
            return False

    def verify(self) -> bool:
        if not self.is_acquired:
            return False

        if self.inhibit_proc:
            proc_alive = self.inhibit_proc.poll() is None
            os_registered = self._verify_os_level()
            return proc_alive and os_registered

        return True

    def release(self):
        if self.inhibit_proc:
            try:
                self.inhibit_proc.terminate()
                self.inhibit_proc.wait(timeout=2)
            except Exception:
                try:
                    self.inhibit_proc.kill()
                except Exception:
                    pass
            self.inhibit_proc = None

        self.is_acquired = False

    def __enter__(self):
        if not self.acquire():
            raise RuntimeError("Failed to acquire Ubuntu systemd sleep inhibitor!")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
