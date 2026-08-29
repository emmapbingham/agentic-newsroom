#!/usr/bin/env python3
"""Derived instrument: per-alias collision-risk flags for derived_client_alias_index.

Entity-resolution hardening item 2 (2026-07-07). The alias index generates
FTS-match strings from clean client names; some bare-token aliases collide
with congressional-press vocabulary or sitting members' surnames (the triangle
screen's VISA->Daines / Miller / Goldman / Schneider false positives). This
script scores every alias with deterministic collision-risk flags so the
morning brief and screens can DOWN-WEIGHT or route around risky aliases. It
does NOT auto-reject anything -- flags inform, humans/sessions decide; the
existing manual rejects stay as-is (status is read, never written here).

Per alias it computes:
  * is_member_surname     -- single-token alias equal (case-insensitive) to any
                             members.last. is_current_member_surname narrows to
                             sitting members (the ones who actually appear in
                             the 2022-2026 press corpus -> the real collision).
  * is_short_common       -- single token AND (len <= 5 OR appears in an English
                             wordlist: /usr/share/dict/words if present, else a
                             small builtin list of the obvious offenders).
  * press_rate_outlier    -- the alias's press_fts phrase-hit count is > 20x the
                             entity's total Senate lobbying-activity count (a
                             disproportion heuristic: a company alias hitting
                             press far more than the company lobbies is probably
                             a common word, not the company).

risk_tier (high/medium/low) folds the flags:
  high   = sitting-member surname, OR any member surname that is also a press
           outlier, OR a short/common word that is also a press outlier.
  medium = any single flag (member surname, short/common, or press outlier)
           not already high.
  low    = no flag.

Deterministic + re-runnable: drops/recreates its own table. Run AFTER the alias
index is rebuilt and the review + manual rejects are applied, and BEFORE (or
independent of) build_derived_client_press_mentions.py.

    python scripts/build_derived_alias_collision_flags.py
    python scripts/build_derived_alias_collision_flags.py --validate
"""
import argparse
import re
import sqlite3
import sys
from pathlib import Path

DB = Path("db/gain.db")
TABLE = "derived_alias_collision_flags"
ALIAS_TABLE = "derived_client_alias_index"
DICT_PATH = Path("/usr/share/dict/words")
PRESS_OUTLIER_FACTOR = 20

# Fallback wordlist if /usr/share/dict/words is absent -- the obvious offenders
# (single common words that read as generic congressional-press vocabulary).
BUILTIN_WORDS = {
    "visa", "shell", "intel", "semi", "penn", "chevron", "apple", "target",
    "gap", "dish", "square", "block", "arm", "meta", "oracle", "sprint",
    "boost", "guardian", "liberty", "progressive", "general", "national",
    "united", "american", "capital", "capitol", "alliance", "coalition",
    "advance", "discover", "care", "health", "energy", "media", "news",
}

DDL = f"""
DROP TABLE IF EXISTS {TABLE};
CREATE TABLE {TABLE} (
    alias_id                  INTEGER PRIMARY KEY,   -- FK -> {ALIAS_TABLE}.id
    entity_id                 INTEGER NOT NULL,
    canonical_name            TEXT NOT NULL,
    alias                     TEXT NOT NULL,
    alias_source              TEXT NOT NULL,
    status                    TEXT NOT NULL,
    n_tokens                  INTEGER NOT NULL,
    press_hits                INTEGER NOT NULL,
    entity_activity_count     INTEGER NOT NULL,
    is_member_surname         INTEGER NOT NULL,
    is_current_member_surname INTEGER NOT NULL,
    is_short_common           INTEGER NOT NULL,
    press_rate_outlier        INTEGER NOT NULL,
    risk_tier                 TEXT NOT NULL CHECK (risk_tier IN ('high','medium','low'))
);
"""
INDEXES = [
    f"CREATE INDEX idx_{TABLE}_entity ON {TABLE}(entity_id);",
    f"CREATE INDEX idx_{TABLE}_tier ON {TABLE}(risk_tier);",
]


def normalize(name: str) -> str:
    n = name.upper().replace(",", "").replace(".", "")
    return re.sub(r"\s+", " ", n).strip()


def fts_phrase(alias: str) -> str:
    return '"' + alias.replace('"', '""') + '"'


def load_wordset():
    if DICT_PATH.exists():
        words = set()
        for line in DICT_PATH.read_text(errors="ignore").splitlines():
            w = line.strip().lower()
            if w and w.isalpha():
                words.add(w)
        return words, str(DICT_PATH)
    return set(BUILTIN_WORDS), "builtin"


def entity_activity_counts(con):
    """entity_id -> total Senate lobbying-activity count, summed over the
    client_ids feeding that entity. The entity's 'raw' aliases are exactly the
    normalized client-name variants that formed the cluster, so map
    normalize(client name) -> client_ids and union per entity."""
    # per-client activity counts
    act_by_client = dict(con.execute(
        "SELECT f.client_id, count(*) FROM senate_filings f "
        "JOIN senate_lobbying_activities a ON a.filing_uuid = f.filing_uuid "
        "GROUP BY f.client_id"
    ).fetchall())
    # normalized client name -> [client_id, ...]
    norm_to_clients = {}
    for cid, name in con.execute("SELECT id, name FROM senate_clients").fetchall():
        norm_to_clients.setdefault(normalize(name), []).append(cid)
    # entity -> set of raw aliases (normalized client names)
    ent_counts = {}
    ent_clients = {}
    for entity_id, alias in con.execute(
        f"SELECT entity_id, alias FROM {ALIAS_TABLE} WHERE alias_source='raw'"
    ).fetchall():
        s = ent_clients.setdefault(entity_id, set())
        for cid in norm_to_clients.get(alias, ()):
            s.add(cid)
    for entity_id, cids in ent_clients.items():
        ent_counts[entity_id] = sum(act_by_client.get(c, 0) for c in cids)
    return ent_counts


def build(con):
    con.executescript(DDL)
    wordset, wordset_src = load_wordset()
    print(f"wordlist source: {wordset_src} ({len(wordset)} words)")

    current_surnames = {r[0] for r in con.execute(
        "SELECT DISTINCT UPPER(last) FROM members WHERE is_current=1 AND last IS NOT NULL AND last<>''"
    ).fetchall()}
    all_surnames = {r[0] for r in con.execute(
        "SELECT DISTINCT UPPER(last) FROM members WHERE last IS NOT NULL AND last<>''"
    ).fetchall()}

    ent_act = entity_activity_counts(con)

    aliases = con.execute(
        f"SELECT id, entity_id, canonical_name, alias, alias_source, status FROM {ALIAS_TABLE}"
    ).fetchall()

    # cache press hit counts by alias string (many entities share e.g. an acronym)
    press_cache = {}

    def press_hits(alias):
        if alias not in press_cache:
            press_cache[alias] = con.execute(
                "SELECT count(*) FROM press_fts WHERE press_fts MATCH ?", (fts_phrase(alias),)
            ).fetchone()[0]
        return press_cache[alias]

    rows = []
    for alias_id, entity_id, canonical_name, alias, alias_source, status in aliases:
        norm = normalize(alias)
        tokens = norm.split(" ") if norm else []
        n_tokens = len(tokens)
        single = n_tokens == 1

        is_curr_surname = int(single and norm in current_surnames)
        is_member_surname = int(single and norm in all_surnames)
        is_short_common = int(single and (len(norm) <= 5 or norm.lower() in wordset))

        hits = press_hits(alias)
        act = ent_act.get(entity_id, 0)
        outlier = int(hits > PRESS_OUTLIER_FACTOR * max(act, 1))

        if is_curr_surname or (is_member_surname and outlier) or (is_short_common and outlier):
            tier = "high"
        elif is_member_surname or is_short_common or outlier:
            tier = "medium"
        else:
            tier = "low"

        rows.append((alias_id, entity_id, canonical_name, alias, alias_source, status,
                     n_tokens, hits, act, is_member_surname, is_curr_surname,
                     is_short_common, outlier, tier))

    con.executemany(
        f"INSERT INTO {TABLE} (alias_id, entity_id, canonical_name, alias, alias_source, "
        f"status, n_tokens, press_hits, entity_activity_count, is_member_surname, "
        f"is_current_member_surname, is_short_common, press_rate_outlier, risk_tier) "
        f"VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", rows)
    for ix in INDEXES:
        con.execute(ix)

    con.execute("DELETE FROM ingest_log WHERE source='alias_collision_flags'")
    con.execute(
        "INSERT INTO ingest_log (source, tier, source_file, record_kind, n_records, ingested_at) "
        "VALUES ('alias_collision_flags','derived','db/gain.db',?,?,datetime('now'))",
        (TABLE, len(rows)))
    con.commit()

    by_tier = dict(con.execute(
        f"SELECT risk_tier, count(*) FROM {TABLE} GROUP BY risk_tier").fetchall())
    by_tier_active = dict(con.execute(
        f"SELECT risk_tier, count(*) FROM {TABLE} WHERE status<>'rejected_too_generic' "
        f"GROUP BY risk_tier").fetchall())
    print(f"built {TABLE}: {len(rows)} alias rows")
    print(f"  all aliases by tier:    {by_tier}")
    print(f"  active aliases by tier: {by_tier_active}")
    report_top20(con)


def report_top20(con):
    # Genuinely-risky active aliases only (>=1 flag, i.e. tier != low), deduped
    # by alias string, ranked by the strong signals first (high tier, sitting
    # surname, press outlier) so a distinctive-but-high-traffic name like
    # "Planned Parenthood" does NOT crowd out real collisions.
    print("\n  top-20 highest-risk currently-active aliases (flagged only, deduped):")
    rows = con.execute(
        f"SELECT alias, min(canonical_name), max(press_hits), max(entity_activity_count), "
        f"max(is_current_member_surname), max(is_member_surname), max(is_short_common), "
        f"max(press_rate_outlier), min(CASE risk_tier WHEN 'high' THEN 0 WHEN 'medium' THEN 1 ELSE 2 END) "
        f"FROM {TABLE} WHERE status<>'rejected_too_generic' AND risk_tier<>'low' "
        f"GROUP BY alias "
        f"ORDER BY min(CASE risk_tier WHEN 'high' THEN 0 WHEN 'medium' THEN 1 ELSE 2 END), "
        f"max(is_current_member_surname) DESC, max(press_rate_outlier) DESC, "
        f"max(is_member_surname) DESC, max(press_hits) DESC LIMIT 20"
    ).fetchall()
    if not rows:
        print("    (none -- all flagged aliases are already rejected)")
    for r in rows:
        tier = {0: 'high', 1: 'medium', 2: 'low'}[r[8]]
        flags = []
        if r[4]: flags.append("current-surname")
        elif r[5]: flags.append("member-surname")
        if r[6]: flags.append("short/common")
        if r[7]: flags.append("press-outlier")
        print(f"    [{tier:6}] {r[0]!r:34} hits={r[2]:<6} act={r[3]:<5} [{','.join(flags)}]  ({r[1]})")


def validate(con):
    ok = True

    def check(label, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  [{'PASS' if cond else 'FAIL'}] {label}")

    n = con.execute(f"SELECT count(*) FROM {TABLE}").fetchone()[0]
    n_alias = con.execute(f"SELECT count(*) FROM {ALIAS_TABLE}").fetchone()[0]
    print(f"  {n} flag rows ({ALIAS_TABLE} has {n_alias})")
    check("one flag row per alias-index row", n == n_alias)
    check("no orphan alias_id",
          con.execute(f"SELECT count(*) FROM {TABLE} t LEFT JOIN {ALIAS_TABLE} a "
                      f"ON a.id=t.alias_id WHERE a.id IS NULL").fetchone()[0] == 0)
    check("every risk_tier in (high,medium,low)",
          con.execute(f"SELECT count(*) FROM {TABLE} WHERE risk_tier NOT IN "
                      f"('high','medium','low')").fetchone()[0] == 0)
    # the manual-reject aliases should score member-surname or short/common
    known = con.execute(
        f"SELECT alias, risk_tier, is_member_surname, is_short_common, press_rate_outlier "
        f"FROM {TABLE} WHERE alias IN ('Miller','Goldman','Schneider','VISA','Shell') "
        f"GROUP BY alias").fetchall()
    print("  known offenders (should be flagged medium/high):")
    for r in known:
        print(f"    {r}")
    check("known surname/word offenders are not tier=low",
          all(r[1] != 'low' for r in known))
    print("PASS" if ok else "FAIL")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true")
    args = ap.parse_args()
    if not DB.exists():
        sys.exit(f"{DB} not found")
    con = sqlite3.connect(DB)
    try:
        if args.validate:
            sys.exit(0 if validate(con) else 1)
        build(con)
    finally:
        con.close()


if __name__ == "__main__":
    main()
