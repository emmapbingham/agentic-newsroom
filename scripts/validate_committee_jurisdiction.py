#!/usr/bin/env python3
"""Validate committee_issue_jurisdiction. Thin wrapper so this stage matches
the build_gain_db.py (ingest script, validate script) convention; the real
reconciliation logic lives in ingest_committee_jurisdiction.py --validate.

    python scripts/validate_committee_jurisdiction.py
"""
import subprocess
import sys

if __name__ == "__main__":
    sys.exit(subprocess.run(
        [sys.executable, "scripts/ingest_committee_jurisdiction.py", "--validate"]
    ).returncode)
