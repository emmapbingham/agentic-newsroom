#!/usr/bin/env python3
"""Validate derived_issue_quarter_volume_press. Thin wrapper matching the
build_gain_db.py (ingest script, validate script) convention -- calls the
build script's own --validate mode instead of rebuilding it a second time.

    python scripts/validate_issue_quarter_volume_press.py
"""
import subprocess
import sys

if __name__ == "__main__":
    sys.exit(subprocess.run(
        [sys.executable, "scripts/build_derived_issue_quarter_volume_press.py", "--validate"]
    ).returncode)
