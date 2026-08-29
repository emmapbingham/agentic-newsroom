#!/usr/bin/env python3
"""Validate member_committees_history. Thin wrapper matching the
build_gain_db.py (ingest script, validate script) convention; the real
reconciliation logic lives in ingest_committee_history.py --validate.

    python scripts/validate_committee_history.py
"""
import subprocess
import sys

if __name__ == "__main__":
    sys.exit(subprocess.run(
        [sys.executable, "scripts/ingest_committee_history.py", "--validate"]
    ).returncode)
