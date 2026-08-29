#!/usr/bin/env python3
"""Validate the press_issue_labels derived instrument (reconciliation). Thin wrapper."""
import sqlite3, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from build_derived_press_issue_labels import DB, validate  # noqa: E402
if not DB.exists():
    sys.exit(f"{DB} not found")
con = sqlite3.connect(DB)
try:
    sys.exit(0 if validate(con) else 1)
finally:
    con.close()
