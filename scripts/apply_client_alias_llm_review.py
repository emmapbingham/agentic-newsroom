#!/usr/bin/env python3
"""One-time apply step: merges the agent-assisted review of derived_client_alias_index
candidate rows back into the table. NOT part of the idempotent rebuild -- run
build_derived_client_alias_index.py first (which wipes the table to
deterministic-only candidates), then this script once, by hand, after the
review file has been produced and read over.

The review was produced by launching batched general-purpose Agent tool
calls (not raw API calls -- see project conversation, 2026-07-06) over the
canonical entity names this table generates at the >=$1M-income threshold.
Each agent returned, per entity: (1) additional alias strings it was
confident a press release would use (abbreviations, legacy brand names)
that the deterministic suffix-strip/FKA-split pass would not produce, and
(2) a generic_flag for any name it judged too ambiguous to safely
FTS-match against press text.

Input format (pipe-delimited, one line per entity):
    entity_id|canonical_name|additional_aliases (semicolon-sep or NONE)|generic_flag (true/false)|reason

The entity_id column is kept for provenance only and is NOT used to match
rows -- entity_id is an autoincrement assigned by clustering order in
build_derived_client_alias_index.py and is NOT stable across a full rebuild
(a rebuild can change which numeric id a given company lands on). This
script matches review rows to table rows by canonical_name instead, which is
stable as long as the deterministic clustering logic that picks the
"longest raw variant" winner doesn't change.

This script:
  1. For generic_flag=true rows, sets status='rejected_too_generic' on ALL
     existing alias rows for that canonical_name's entity_id (raw/suffix_strip/
     fka_split) -- the agent judged the ENTITY's name space unsafe to
     FTS-match at all, not just one alias string.
  2. For additional_aliases, normalizes each suggested string the same way
     the builder does (upper/strip punctuation/collapse whitespace) and
     inserts it as alias_source='llm_suggested', status='candidate' --
     UNLESS that normalized string already exists for the entity (dedup
     against suffix_strip/fka_split output), or the entity was flagged
     generic in step 1 (skip suggesting new aliases for an entity already
     rejected).

A canonical_name in the review file with no matching row in the table is
reported as skipped (this can happen if a rebuild changed which raw name
variant won as canonical_name for that cluster).

Requires manual review of the input file before running -- this script
trusts the file's judgments verbatim, it does not re-derive them.

    python scripts/apply_client_alias_llm_review.py <review_file.txt>
    python scripts/apply_client_alias_llm_review.py <review_file.txt> --dry-run
"""
import argparse
import re
import sqlite3
import sys
from pathlib import Path

DB = Path("db/gain.db")
TABLE = "derived_client_alias_index"


def normalize(name: str) -> str:
    n = name.upper()
    n = n.replace(",", "").replace(".", "")
    n = re.sub(r"\s+", " ", n).strip()
    return n


def parse_review_file(path: Path):
    rows = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("|")
        if len(parts) < 4:
            print(f"WARNING: skipping malformed line: {line!r}", file=sys.stderr)
            continue
        entity_id = int(parts[0])
        canonical_name = parts[1]
        aliases_raw = parts[2].strip()
        generic_flag = parts[3].strip().lower() == "true"
        reason = parts[4] if len(parts) > 4 else ""
        aliases = [] if aliases_raw.upper() == "NONE" else [
            a.strip() for a in aliases_raw.split(";") if a.strip()
        ]
        rows.append((entity_id, canonical_name, aliases, generic_flag, reason))
    return rows


def apply(con, rows, dry_run=False):
    n_rejected_entities = 0
    n_new_aliases = 0
    n_skipped_dupe = 0
    n_skipped_not_found = 0

    for _file_entity_id, canonical_name, aliases, generic_flag, reason in rows:
        # Look up the CURRENT entity_id for this canonical_name -- the file's
        # own entity_id column is not trustworthy across a rebuild, see docstring.
        # Try an exact canonical_name match first; if the table has since
        # merged this entity into a differently-named cluster (e.g. an
        # FKA-pair merge -- see build_derived_client_alias_index.py), fall
        # back to matching the review's canonical_name against the entity's
        # existing alias set (every raw name variant that fed the cluster is
        # kept as a 'raw' alias, so this recovers the right entity_id without
        # a loose/ambiguous substring guess).
        match = con.execute(
            f"SELECT DISTINCT entity_id FROM {TABLE} WHERE canonical_name=?",
            (canonical_name,),
        ).fetchall()
        if not match:
            match = con.execute(
                f"SELECT DISTINCT entity_id FROM {TABLE} WHERE alias=? AND alias_source='raw'",
                (normalize(canonical_name),),
            ).fetchall()
        if not match:
            n_skipped_not_found += 1
            print(f"WARNING: canonical_name {canonical_name!r} not found in "
                  f"{TABLE} (checked canonical_name and raw aliases), skipping",
                  file=sys.stderr)
            continue
        if len(match) > 1:
            print(f"WARNING: canonical_name {canonical_name!r} matches multiple "
                  f"entity_ids {[m[0] for m in match]}, skipping (ambiguous)",
                  file=sys.stderr)
            continue
        entity_id = match[0][0]

        if generic_flag:
            n_rejected_entities += 1
            if not dry_run:
                con.execute(
                    f"UPDATE {TABLE} SET status='rejected_too_generic', "
                    f"review_note=? WHERE entity_id=? AND status='candidate'",
                    (f"llm_review: {reason}", entity_id),
                )
            continue

        existing = {
            r[0] for r in con.execute(
                f"SELECT alias FROM {TABLE} WHERE entity_id=?", (entity_id,)
            ).fetchall()
        }
        existing_norm = {normalize(a) for a in existing}

        row = con.execute(
            f"SELECT total_income, n_client_ids, norm_name FROM {TABLE} "
            f"WHERE entity_id=? LIMIT 1", (entity_id,)
        ).fetchone()
        total_income, n_client_ids, norm_name = row

        for alias in aliases:
            norm_alias = normalize(alias)
            if norm_alias in existing_norm:
                n_skipped_dupe += 1
                continue
            existing_norm.add(norm_alias)
            n_new_aliases += 1
            if not dry_run:
                con.execute(
                    f"INSERT INTO {TABLE} (entity_id, canonical_name, norm_name, alias, "
                    f"alias_source, status, total_income, n_client_ids, review_note) "
                    f"VALUES (?,?,?,?,?,?,?,?,?)",
                    (entity_id, canonical_name, norm_name, alias, "llm_suggested",
                     "candidate", total_income, n_client_ids, f"llm_review: {reason}"),
                )

    if not dry_run:
        con.commit()

    print(f"{'[dry run] ' if dry_run else ''}entities flagged too-generic (existing rows "
          f"marked rejected_too_generic): {n_rejected_entities}")
    print(f"{'[dry run] ' if dry_run else ''}new llm_suggested aliases inserted: {n_new_aliases}")
    print(f"suggested aliases skipped as duplicates of existing rows: {n_skipped_dupe}")
    print(f"review rows skipped, canonical_name not found in current table: {n_skipped_not_found}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("review_file", type=Path)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if not DB.exists():
        sys.exit(f"{DB} not found")
    if not args.review_file.exists():
        sys.exit(f"{args.review_file} not found")

    rows = parse_review_file(args.review_file)
    con = sqlite3.connect(DB)
    try:
        apply(con, rows, dry_run=args.dry_run)
    finally:
        con.close()


if __name__ == "__main__":
    main()
