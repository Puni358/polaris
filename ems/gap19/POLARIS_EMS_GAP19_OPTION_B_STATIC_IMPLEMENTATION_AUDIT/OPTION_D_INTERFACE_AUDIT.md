# Option D Interface Audit

- Ingests `config["operating_mode"]`.
- Supports `NORMAL` and `EMERGENCY` modes.
- In `EMERGENCY` mode, restricts battery discharge to protected critical load ($P_{\text{dis}}[t] \le P_{\text{served}}[t]$).
- Upstream authority retained by ECD (optimizer does not set mode autonomously).

`OPTION_D_INTERFACE = PASS`
