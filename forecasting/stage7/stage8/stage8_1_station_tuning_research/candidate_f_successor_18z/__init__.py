"""
Isolated Candidate F successor fetcher package (18Z LWP/IWP causal replacement).

STATUS: implementation + offline tests only. No network request has ever been made by
running this package's test suite or by writing this code. Nothing in this package is
imported by, or imports, the frozen experiment, Candidate F model, or any existing
feature-matrix build script. See DESIGN.md in this directory for the full specification
this package implements: ../CANDIDATE_F_SUCCESSOR_18Z_FEATURE_CONTRACT_v1.md and
../CANDIDATE_F_SUCCESSOR_CLEAN_SPLIT_PROTOCOL_v1.md.

Importing this package performs no I/O and makes no network call.
"""
