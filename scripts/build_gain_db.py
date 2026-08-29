"""Build db/gain.db from scratch, in dependency order.

The single command that reproduces the whole corpus. Stages run in order because
later stages depend on earlier ones:

  raw sources  (independent):  senate, house, press
  reference    (depends on senate): members  -- honoree_member_map reads
                                               senate_contribution_items
  reference    (depends on members): committee_jurisdiction  -- hand-curated
                                      committee->issue-code map, needs
                                      committees + ref_issue_codes to exist
  reference    (depends on members): committee_history  -- point-in-time
                                      committee rosters from pinned git
                                      history snapshots (member_committees is
                                      current-Congress-only; this covers
                                      2022-2026 across Congress transitions)
  derived      (future marts):  build_*.py reading only gain.db tables

Each stage is itself source-scoped + idempotent, so this is safe to re-run and
you can also run any single ingester directly. Lineage is recorded in
ingest_log.tier (raw | reference | derived).

Usage:
    python scripts/build_gain_db.py                 # full build
    python scripts/build_gain_db.py --validate       # build, then run validators
    python scripts/build_gain_db.py --only members   # one stage
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path

DB = Path("db/gain.db")

# (stage name, tier, ingest script, validate script)
STAGES = [
    ("senate",        "raw",       "scripts/ingest_senate.py",            "scripts/validate_senate.py"),
    ("house",         "raw",       "scripts/ingest_house.py",             "scripts/validate_house.py"),
    ("press",         "raw",       "scripts/ingest_press.py",             "scripts/validate_press.py"),
    ("members",       "reference", "scripts/ingest_members.py",           "scripts/validate_members.py"),
    ("committee_jurisdiction", "reference", "scripts/ingest_committee_jurisdiction.py", "scripts/validate_committee_jurisdiction.py"),
    ("committee_history", "reference", "scripts/ingest_committee_history.py", "scripts/validate_committee_history.py"),
    ("cross_chamber",     "derived", "scripts/build_derived_cross_chamber.py",     "scripts/validate_cross_chamber.py"),
    ("registrant_income", "derived", "scripts/build_derived_registrant_income.py", "scripts/validate_registrant_income.py"),
    ("registrant_issue",  "derived", "scripts/build_derived_registrant_issue.py",  "scripts/validate_registrant_issue.py"),
    ("member_contributions","derived","scripts/build_derived_member_contributions.py","scripts/validate_member_contributions.py"),
    ("issue_quarter_volume_press", "derived", "scripts/build_derived_issue_quarter_volume_press.py", "scripts/validate_issue_quarter_volume_press.py"),
    ("committee_quarter_press", "derived", "scripts/build_derived_committee_quarter_press.py", "scripts/validate_committee_quarter_press.py"),
]


def run(script, args=()):
    cmd = [sys.executable, script, *args]
    print(f"\n$ {' '.join(cmd)}", flush=True)
    t = time.time()
    r = subprocess.run(cmd)
    if r.returncode != 0:
        sys.exit(f"FAILED: {script} (exit {r.returncode})")
    print(f"  ({time.time()-t:.0f}s)")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", help="run a single stage by name")
    ap.add_argument("--validate", action="store_true", help="run validators after building")
    args = ap.parse_args()

    stages = [s for s in STAGES if not args.only or s[0] == args.only]
    if not stages:
        sys.exit(f"unknown stage {args.only!r}; choose from {[s[0] for s in STAGES]}")

    # A full build is a from-scratch rebuild: wipe so shared-schema changes
    # (e.g. new ingest_log columns) take effect. --only refreshes one stage
    # in place and leaves the rest untouched (source-scoped).
    if not args.only and DB.exists():
        print(f"removing {DB} for a from-scratch build")
        DB.unlink()

    t0 = time.time()
    for name, tier, ingest, _ in stages:
        print(f"\n=== stage: {name} ({tier}) ===")
        run(ingest)
    if args.validate:
        print("\n=== validation ===")
        for name, _, _, validate in stages:
            extra = ["--reconcile"] if name in ("senate", "press") else []
            run(validate, extra)
    print(f"\nbuild complete in {time.time()-t0:.0f}s -> db/gain.db")


if __name__ == "__main__":
    main()
