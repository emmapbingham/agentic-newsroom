#!/usr/bin/env python3
"""Validate the member_contributions derived instrument. Thin wrapper."""
import sqlite3, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from build_derived_member_contributions import DB, validate  # noqa: E402
if not DB.exists():
    sys.exit(f"{DB} not found")
con = sqlite3.connect(DB)
try:
    sys.exit(0 if validate(con) else 1)
finally:
    con.close()
