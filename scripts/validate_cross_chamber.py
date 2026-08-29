#!/usr/bin/env python3
"""Validate the cross-chamber derived instrument — reconciliation only.

Thin wrapper so the derived stage matches the per-stage validator convention
used by build_gain_db.py. The real logic lives in build_derived_cross_chamber.
"""
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build_derived_cross_chamber import DB, validate  # noqa: E402

if not DB.exists():
    sys.exit(f"{DB} not found")
con = sqlite3.connect(DB)
try:
    sys.exit(0 if validate(con) else 1)
finally:
    con.close()
