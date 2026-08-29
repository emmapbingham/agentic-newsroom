#!/usr/bin/env python3
"""Derived instrument: normalized name + alias index for high-spend Senate clients.

First stage of the press-mining entity-tracing pipeline (data_manual.md's
"entity graph" lead: press NER -> companies/orgs -> LDA registrants/clients ->
government entities -> committees -> members). Rather than NER over press
text, this goes the other direction: starts from the corpus's own clean
client names (high income, i.e. worth tracing) and generates alias strings to
FTS-match against press_fts (derived_client_press_mentions, a later stage).

This table is deterministic only -- suffix stripping and FKA/DBA splitting.
It does NOT filter aliases by length/genericness ("3M", "GM", "AIG" are all
short and all safe); genericness judgment is deferred to a manual + agent-
assisted review pass (see reference/README or the newsroom screen notes) that
flags unsafe aliases *after* seeing the full candidate list, rather than a
blind character-count cutoff before review. Approved additions from that
review get applied via a separate step (not idempotent-rebuild -- see below).

Grain: many rows per entity (one per alias). Entities are Senate clients
collapsed by a suffix-stripped core name key (normalize: strip
periods/commas, collapse whitespace, uppercase; then strip corporate
suffixes repeatedly down to a stable core) among clients with >= $1M total
reported income 2022-2026Q1. This deliberately reuses the same
name-collapsing idea that revealed Comcast Corporation fragmenting into 52
client_ids (docs/derived_db.md income-integrity discussion) rather than
solving general entity resolution -- but clusters on the stripped core, not
the raw normalized name, so "X Corporation" and "X" (same company, one
client record omits the suffix) land in one entity, not two.

Clustering also strips an FKA/FORMERLY/DBA parenthetical before computing the
core key, so "X" and "X (FKA Y)" land in one entity too (found 2026-07-06:
AT&T Services, Inc. vs AT&T Services, Inc. (FKA AT&T) were splitting real
income+press-mention totals across two entity_ids -- 26 of 77 FKA-marked
canonical names had an exact-match plain-name sibling entity this way).
This is a narrow, evidence-backed merge: the filer's own filing asserts the
identity ("formerly known as"), it is not a general fuzzy-name-similarity
merge -- unrelated similarly-named companies (e.g. "Johnson Controls" vs
"Johnson & Johnson") are NOT touched by this, since neither carries an FKA
marker pointing at the other. A separate, non-FKA prefix-sharing case
(Fresenius Medical Care vs Fresenius Medical Care North America) was found
in the same session and deliberately NOT merged here -- confirming that one
is genuinely the same operation vs. a distinct subsidiary needs corroborating
evidence (shared registrant/lobbyists), not a naming heuristic.

CAVEAT: the LOC COMMUNITY ASSOCIATION crank filer (confirmed 2026-07-04,
derived_registrant_income_integrity) reports a flat fabricated $20M/quarter
and sits at the very top of this table's income ranking ($180M total). Any
consumer ranking by total_income must exclude or flag it -- it is real
income-integrity noise, not a tracing target.

    python scripts/build_derived_client_alias_index.py
    python scripts/build_derived_client_alias_index.py --validate
"""
import argparse
import re
import sqlite3
import sys
from pathlib import Path

DB = Path("db/gain.db")
TABLE = "derived_client_alias_index"
MIN_TOTAL_INCOME = 1_000_000

# Fixed suffix list, stripped only from the END of the (already comma/period
# -stripped, upper-cased) name. Order matters: longer/more-specific forms
# before shorter substrings they contain (e.g. "CORPORATION" before "CORP").
SUFFIXES = [
    "INCORPORATED", "CORPORATION", "COMPANY", "LIMITED",
    "LLC", "L L C", "LLP", "L L P", "LP", "L P",
    "PLLC", "PLC", "INC", "CORP", "CO", "LTD",
]

FKA_DBA_RE = re.compile(
    r"^(?P<primary>.*?)\s*[\(/]\s*(?:F/?K/?A|FORMERLY(?: KNOWN AS)?|D/?B/?A|DOING BUSINESS AS)\s*[:\s]*"
    r"(?P<alt>[^\)]+)\)?\s*$",
    re.IGNORECASE,
)


def normalize(name: str) -> str:
    n = name.upper()
    n = n.replace(",", "").replace(".", "")
    n = re.sub(r"\s+", " ", n).strip()
    return n


def strip_suffix(norm_name: str) -> str | None:
    for suf in SUFFIXES:
        pattern = r"^(.*\S)\s+" + suf + r"$"
        m = re.match(pattern, norm_name)
        if m and m.group(1) != norm_name:
            return m.group(1).strip()
    return None


def split_fka_dba(raw_name: str):
    m = FKA_DBA_RE.match(raw_name)
    if not m:
        return None
    primary = normalize(m.group("primary"))
    alt = normalize(m.group("alt"))
    return primary, alt


# --- Stage-2 cluster merge (2026-07-07, entity-resolution hardening) ---------
# The core_key clustering above collapses corporate-suffix and paren-FKA
# variants, but NOT: (a) apostrophe/punctuation-only spelling differences
# ("AMERICA'S" vs "AMERICAS", "BRISTOL MYERS" vs "BRISTOL-MYERS"); (b) acronym
# parentheticals ("... (AHIP)"); (c) "(AND SUBSIDIARIES)"; (d) non-parenthetical
# formerly/dba markers ("CVS PREVIOUSLY AETNA", "... INC DBA AMERICAS CREDIT
# UNIONS"). Those left CVS as 3 entities and America's Credit Unions as 2,
# splitting money + press-mention totals across ids. This stage merges cluster
# keys by a punctuation/apostrophe-normalized token set, with token-SUBSET
# matching for marker-shortened variants -- deliberately conservative:
#   * only *noise* parentheticals are dropped (acronyms + subsidiary/FKA
#     markers); an identity-bearing parenthetical like "(ON BEHALF OF
#     GENENTECH INC)" is KEPT, so consultant filings for different clients
#     (Tiber Creek OBO Genentech vs OBO Novartis) do NOT collapse;
#   * a strict-subset merge (A's tokens < B's) fires only when A is a
#     marker-shortened variant, and never into/out of an "on behalf of"
#     (OBO) coalition/consultant filing;
#   * equal-token merges are safe by construction (the two clusters differed
#     only in punctuation/paren/marker position -- otherwise core_key would
#     already have unified them).
# Preserves the existing FKA-split alias logic downstream unchanged.
MARKER_CUT_RE = re.compile(
    r"\s+(?:F/?K/?A|FKA|FORMERLY(?:\s+KNOWN\s+AS|\s+REPORTED\s+AS)?|"
    r"PREVIOUSLY(?:\s+REPORTED\s+AS|\s+KNOWN\s+AS)?|D/?B/?A|DBA|"
    r"DOING\s+BUSINESS\s+AS|N/?K/?A|NKA)\s+.*$", re.IGNORECASE)
SUBS_RE = re.compile(
    r"\s+AND\s+(?:VARIOUS\s+|ITS\s+|CERTAIN\s+|RELATED\s+)?"
    r"(?:SUBSIDIARIES|AFFILIATES|AFFILIATED\s+ENTITIES)\b.*$", re.IGNORECASE)
OBO_RE = re.compile(r"\b(?:OBO|O/?B/?O|ON\s+BEHALF\s+OF)\b", re.IGNORECASE)
PAREN_MARKER_RE = re.compile(
    r"^\s*(?:AND\s+(?:VARIOUS\s+|ITS\s+|CERTAIN\s+|RELATED\s+)?(?:SUBSIDIARIES|AFFILIATES)"
    r"|F/?K/?A|FKA|FORMERLY|PREVIOUSLY|D/?B/?A|DBA|N/?K/?A|NKA)\b", re.IGNORECASE)


def _paren_is_noise(content: str) -> bool:
    """A parenthetical is mergeable noise iff it is an acronym-like single
    token (<=7 alnum chars, e.g. (AHIP), (PCMA), ("EPC")) or a subsidiary/FKA
    marker. Multi-word content -- (ON BEHALF OF GENENTECH INC), (A SUBSIDIARY
    OF PFIZER) -- carries distinguishing identity and is KEPT."""
    if PAREN_MARKER_RE.match(content):
        return True
    bare = re.sub(r"[^A-Za-z0-9]", "", content)
    tokens = [t for t in re.sub(r"[^A-Za-z0-9 ]", " ", content).split() if t]
    return len(tokens) == 1 and 0 < len(bare) <= 7


def merge_tokens(core: str) -> frozenset:
    """Punctuation/apostrophe-normalized token set used for stage-2 merging,
    with noise parentheticals and formerly/dba markers removed."""
    s = re.sub(r"\(([^)]*)\)",
               lambda m: " " if _paren_is_noise(m.group(1)) else " " + m.group(1) + " ",
               core)
    s = MARKER_CUT_RE.sub("", s)
    s = SUBS_RE.sub("", s)
    s = s.replace("'", "")
    s = re.sub(r"[^A-Z0-9& ]", " ", s.upper())
    s = re.sub(r"\s+", " ", s).strip()
    return frozenset(t for t in s.split(" ") if t)


def core_tokens(core: str) -> frozenset:
    """Token set of the raw core key (no marker stripping) -- used to detect
    whether merge_tokens dropped tokens, i.e. this is a marker-shortened
    variant eligible for a strict-subset merge."""
    s = core.replace("'", "")
    s = re.sub(r"[^A-Z0-9& ]", " ", s.upper())
    return frozenset(t for t in re.sub(r"\s+", " ", s).strip().split(" ") if t)


def merge_clusters(eligible: dict):
    """Second-stage merge over the income-eligible clusters. Returns
    (targets, merge_log): targets maps a surviving cluster key -> combined
    cluster dict; merge_log is a list of (absorbed_key, target_key)."""
    info = {}
    for k in eligible:
        mt = merge_tokens(k)
        ct = core_tokens(k)
        info[k] = (mt, bool(mt) and mt < ct)  # (tokens, is marker-shortened)

    # Larger token sets first (so a subset is always seen after its superset),
    # then higher income, then key -- fully deterministic.
    order = sorted(eligible, key=lambda k: (-len(info[k][0]), -eligible[k]["total_income"], k))

    targets: dict = {}
    target_tokens: dict = {}
    merge_log = []

    for k in order:
        mt, has_marker = info[k]
        best = None
        if mt:
            a_obo = bool(OBO_RE.search(k))
            for t, tt in target_tokens.items():
                if not (mt <= tt):
                    continue
                ok = (mt == tt) or (has_marker and not a_obo and not OBO_RE.search(t))
                if not ok:
                    continue
                # most specific (fewest-token) superset wins; ties -> key asc
                if (best is None or len(tt) < len(target_tokens[best])
                        or (len(tt) == len(target_tokens[best]) and t < best)):
                    best = t
        if best is not None:
            tc, sc = targets[best], eligible[k]
            tc["total_income"] += sc["total_income"]
            tc["client_ids"] |= sc["client_ids"]
            tc["names"] |= sc["names"]
            tc["norm_names"] |= sc["norm_names"]
            merge_log.append((k, best))
        else:
            targets[k] = {
                "total_income": eligible[k]["total_income"],
                "client_ids": set(eligible[k]["client_ids"]),
                "names": set(eligible[k]["names"]),
                "norm_names": set(eligible[k]["norm_names"]),
            }
            target_tokens[k] = mt
    return targets, merge_log


DDL = f"""
DROP TABLE IF EXISTS {TABLE};
CREATE TABLE {TABLE} (
    id                 INTEGER PRIMARY KEY,
    entity_id          INTEGER NOT NULL,   -- groups rows for one collapsed entity
    canonical_name      TEXT NOT NULL,      -- longest raw client name variant in the cluster
    norm_name          TEXT NOT NULL,      -- the normalized cluster key
    alias              TEXT NOT NULL,
    alias_source       TEXT NOT NULL CHECK (alias_source IN
                        ('raw','suffix_strip','fka_split','llm_suggested')),
    status             TEXT NOT NULL DEFAULT 'candidate'
                        CHECK (status IN ('candidate','approved','rejected_too_generic')),
    total_income       REAL NOT NULL,
    n_client_ids       INTEGER NOT NULL,
    review_note        TEXT
);
"""

INDEXES = [
    f"CREATE INDEX idx_{TABLE}_entity ON {TABLE}(entity_id);",
    f"CREATE UNIQUE INDEX idx_{TABLE}_alias ON {TABLE}(entity_id, alias, alias_source);",
]


def build(con):
    con.executescript(DDL)

    rows = con.execute(
        """
        SELECT sc.id AS client_pk, sc.name
        FROM senate_clients sc
        """
    ).fetchall()

    # senate_filings.client_id is the FK to senate_clients.id (the
    # fine-grained per-record key) -- NOT to senate_clients.client_id, which
    # docs/senate_db.md documents as "kept as a column for later
    # entity-resolution, not the key" and is in practice massively
    # collision-prone (e.g. client_id=12 is shared by 3,556 distinct company
    # names corpus-wide). First build of this script keyed the income lookup
    # by client_id and looked it up via senate_clients.client_id, silently
    # pulling in other companies' income for any senate_clients row whose
    # client_id != id (caught 2026-07-06 while manually checking Norfolk
    # Southern -- correct total is $4,714,000 across 2022-2026Q1, table had
    # $1,180,000). Group by senate_clients.id (client_pk) throughout.
    income_by_client_pk = dict(
        con.execute(
            "SELECT client_id, SUM(income_amt) FROM senate_filings "
            "WHERE income_amt IS NOT NULL AND income_amt > 0 GROUP BY client_id"
        ).fetchall()
    )

    # Cluster on the FULLY suffix-stripped form, not the raw normalized name.
    # Otherwise "NORFOLK SOUTHERN CORPORATION" and "NORFOLK SOUTHERN" (same
    # company, one client record omits the corporate suffix) land in two
    # separate entities -- caught 2026-07-06 alongside the client_id bug
    # above: it split Norfolk Southern's $4.71M into a $3.59M cluster and a
    # $1.12M cluster. Stripping to a stable core key before grouping fixes
    # this; the un-stripped norm_name is still recorded per name variant and
    # still generates its own "raw" alias for FTS-matching.
    def core_key(norm_name: str) -> str:
        core = norm_name
        while True:
            stripped = strip_suffix(core)
            if not stripped:
                return core
            core = stripped

    clusters: dict[str, dict] = {}
    for client_pk, name in rows:
        total = income_by_client_pk.get(client_pk)
        if not total:
            continue
        norm_name = normalize(name)
        # Cluster on the FKA/FORMERLY/DBA "primary" name when present, so
        # "X" and "X (FKA Y)" collapse into one entity instead of splitting
        # income/mentions across two -- see docstring caveat.
        split = split_fka_dba(name)
        key_source = split[0] if split else norm_name
        key = core_key(key_source)
        c = clusters.setdefault(key, {
            "total_income": 0.0, "client_ids": set(), "names": set(), "norm_names": set(),
        })
        c["total_income"] += total
        c["client_ids"].add(client_pk)
        c["names"].add(name)
        c["norm_names"].add(norm_name)

    # Income filter first, then stage-2 merge over the eligible clusters so
    # money/mention totals split across punctuation/marker variants (CVS x3,
    # America's Credit Unions x2, ...) land on one entity. Merging within the
    # eligible set (not all ~23k clusters) keeps the emitted entity set aligned
    # with the >=$1M review coverage and matches the "count decreases modestly"
    # sanity bound below.
    eligible = {k: c for k, c in clusters.items() if c["total_income"] >= MIN_TOTAL_INCOME}
    n_pre_merge = len(eligible)
    targets, merge_log = merge_clusters(eligible)
    n_post_merge = len(targets)

    # Log every merge (absorbed -> target) with names, per spec.
    print(f"stage-2 merge: {n_pre_merge} eligible clusters -> {n_post_merge} entities "
          f"({len(merge_log)} merged away)")
    for absorbed_key, target_key in sorted(merge_log):
        a_names = sorted(eligible[absorbed_key]["names"])
        b_names = sorted(targets[target_key]["names"])
        print(f"  MERGE absorbed {absorbed_key!r} {a_names}")
        print(f"        into     {target_key!r} (canonical cluster now: {b_names})")

    # --- acceptance asserts (spec item 1) -----------------------------------
    name_to_target = {}
    for tkey, tc in targets.items():
        for nm in tc["names"]:
            name_to_target[nm] = tkey
    cvs_names = ["CVS HEALTH INC", "CVS HEALTH (AND SUBSIDIARIES)", "CVS PREVIOUSLY AETNA"]
    cvs_targets = {name_to_target.get(n) for n in cvs_names}
    assert None not in cvs_targets and len(cvs_targets) == 1, (
        f"acceptance FAIL: CVS variants did not collapse to one entity: "
        f"{ {n: name_to_target.get(n) for n in cvs_names} }")
    acu_names = [n for n in name_to_target if "AMERICA" in n.upper()
                 and "CREDIT UNION" in n.upper()]
    acu_targets = {name_to_target[n] for n in acu_names}
    assert len(acu_names) >= 2 and len(acu_targets) == 1, (
        f"acceptance FAIL: America's/Americas Credit Unions did not collapse to "
        f"one entity: { {n: name_to_target[n] for n in acu_names} }")
    assert n_post_merge < n_pre_merge, (
        f"acceptance FAIL: merge did not reduce entity count "
        f"({n_pre_merge} -> {n_post_merge})")
    assert n_post_merge >= 1800, (
        f"STOP: entity count collapsed to {n_post_merge} (< 1800 floor) -- merge key "
        f"is too loose, refusing to ship an over-merged index")
    print(f"  [PASS] CVS -> 1 entity; America's Credit Unions -> 1 entity; "
          f"count {n_pre_merge} -> {n_post_merge} (>= 1800 floor)")

    entity_id = 0
    insert_rows = []
    for c in targets.values():
        entity_id += 1
        canonical_name = max(c["names"], key=lambda s: (len(s), s))
        norm_name = max(c["norm_names"], key=lambda s: (len(s), s))
        total_income = c["total_income"]
        n_client_ids = len(c["client_ids"])

        seen_aliases = set()

        def add(alias, source):
            key = (alias, source)
            if alias and key not in seen_aliases:
                seen_aliases.add(key)
                insert_rows.append((
                    entity_id, canonical_name, norm_name, alias, source,
                    "candidate", total_income, n_client_ids, None,
                ))

        for nn in c["norm_names"]:
            add(nn, "raw")

        stripped = strip_suffix(norm_name)
        if stripped:
            add(stripped, "suffix_strip")
            second = strip_suffix(stripped)
            if second:
                add(second, "suffix_strip")

        for raw_name in c["names"]:
            split = split_fka_dba(raw_name)
            if split:
                primary, alt = split
                add(primary, "fka_split")
                add(alt, "fka_split")

    con.executemany(
        f"INSERT INTO {TABLE} (entity_id, canonical_name, norm_name, alias, alias_source, "
        f"status, total_income, n_client_ids, review_note) VALUES (?,?,?,?,?,?,?,?,?)",
        insert_rows,
    )
    for ix in INDEXES:
        con.execute(ix)

    n_entities = entity_id
    n_rows = len(insert_rows)
    con.execute("DELETE FROM ingest_log WHERE source='client_alias_index'")
    con.execute(
        "INSERT INTO ingest_log (source, tier, source_file, record_kind, n_records, ingested_at) "
        "VALUES ('client_alias_index','derived','db/gain.db',?,?,datetime('now'))",
        (TABLE, n_rows),
    )
    con.commit()
    print(f"built {TABLE}: {n_entities} entities, {n_rows} candidate alias rows "
          f"(threshold >= ${MIN_TOTAL_INCOME:,.0f} total income)")


def validate(con):
    ok = True

    def check(label, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  [{'PASS' if cond else 'FAIL'}] {label}")

    n_entities = con.execute(f"SELECT count(DISTINCT entity_id) FROM {TABLE}").fetchone()[0]
    n_rows = con.execute(f"SELECT count(*) FROM {TABLE}").fetchone()[0]
    print(f"  {n_entities} entities, {n_rows} alias rows")

    check("every entity has at least a raw alias",
          con.execute(
              f"SELECT count(*) FROM (SELECT entity_id FROM {TABLE} GROUP BY entity_id "
              f"HAVING sum(alias_source='raw') = 0)"
          ).fetchone()[0] == 0)

    dupe = con.execute(
        f"SELECT count(*) FROM (SELECT entity_id, alias, alias_source, count(*) c "
        f"FROM {TABLE} GROUP BY entity_id, alias, alias_source HAVING c > 1)"
    ).fetchone()[0]
    check("no duplicate (entity_id, alias, alias_source) rows", dupe == 0)

    loc = con.execute(
        f"SELECT total_income FROM {TABLE} WHERE canonical_name LIKE '%LOC NATION%' LIMIT 1"
    ).fetchone()
    check("known crank filer (LOC NATION) present and flagged in docstring caveat "
          "-- confirm consumers exclude/flag it, not this table's job",
          loc is not None)
    if loc:
        print(f"  LOC NATION total_income = {loc[0]:,.0f} (crank, see build_derived_registrant_income_integrity)")

    sample = con.execute(
        f"SELECT canonical_name, alias, alias_source FROM {TABLE} "
        f"WHERE alias_source='suffix_strip' ORDER BY total_income DESC LIMIT 5"
    ).fetchall()
    print("  sample suffix-stripped aliases (highest income entities):")
    for row in sample:
        print(f"    {row}")

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
