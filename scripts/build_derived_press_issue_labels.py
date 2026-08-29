#!/usr/bin/env python3
"""Derived table: which LDA issue codes a press release is about.

Replaces the LIKE-match ISSUE_KEYWORDS map with a logistic-regression
classifier trained on Senate/House LDA activity descriptions (see
scripts/press_topic_classifier.py for the full method, the model-selection
history -- hand-rolled TF-IDF, then sklearn TF-IDF-centroid, then this --
and docs/press-issue-classifier.md for the
audit that motivated the replacement).

Grain: (release_id, issue_code) -- one row per release-code pair whose
predicted probability clears the global threshold. Deliberately
one-release-to-MANY-codes (a release can and does match multiple codes),
matching the semantics ISSUE_KEYWORDS already had and that all three
downstream consumer tables already assume
(derived_issue_quarter_volume_press, derived_committee_quarter_press,
derived_member_press_topic_panel).

Threshold: ONE global probability cutoff (PROBABILITY_THRESHOLD = 0.3),
not per-code. This is a direct consequence of switching from cosine-
similarity-to-centroid to logistic regression's predict_proba: cosine
similarity has no natural cross-code scale (a "good" INS score and a
"good" ENV score sit at very different absolute values, which is why the
centroid approach needed per-code thresholds and still couldn't serve
both TAX's recall and ENV's precision at once -- see press_topic_classifier
module docstring for that history). predict_proba IS cross-code-comparable
by construction (one-vs-rest logistic regression normalizes each class's
score against the others), so a single global cutoff works. Validated by
a threshold sweep (0.15-0.60) across INS/TAX/ENV/VET/CPT/PHA/HCR/IMM/AGR/
MON/TOB plus hand-checked precision at 0.3 for ENV/VET/TAX/CPT -- clean,
on-topic top matches for all, no repeat of the centroid approach's
false-positive pattern (generic legislative-process press).

is_primary: the single highest-probability code for a release is flagged
is_primary=1 (a free argmax/single-label column from the same
predict_proba matrix -- for consumers that want "the one topic" rather
than the full multi-label set). A release with zero codes above threshold
has no rows in this table at all (and therefore no primary either) -- this
is correct, not a bug: see the multi-label validation in the plan doc,
where generic partisan rhetoric with no policy substance correctly
produced zero labels, a real precision improvement over LIKE-matching bare
"health"/"tax" substrings.

Excluded codes: GOV, MIA, SCI, CON (see press_topic_classifier.EXCLUDED_CODES)
-- confirmed this session that TF-IDF-against-LDA-descriptions does not
solve the "too generic to disambiguate" problem any better than keywords did.

low_confidence: flags rows for codes with fewer than
press_topic_classifier.LOW_TRAIN_VOLUME activity descriptions -- not enough
training signal to trust the classifier's decision boundary for that code
the same way as a well-populated code.

    python scripts/build_derived_press_issue_labels.py
    python scripts/build_derived_press_issue_labels.py --validate
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from press_topic_classifier import PressTopicClassifier  # noqa: E402

DB = Path("db/gain.db")
TABLE = "derived_press_issue_labels"
BATCH_SIZE = 2000

# Global predict_proba cutoff -- see module docstring for the sweep/spot-
# check evidence behind this value.
PROBABILITY_THRESHOLD = 0.3


def build_ddl(table: str) -> str:
    return f"""
DROP TABLE IF EXISTS {table};
CREATE TABLE {table} (
    release_id      INTEGER NOT NULL,
    issue_code      TEXT    NOT NULL,
    probability     REAL    NOT NULL,
    is_primary      INTEGER NOT NULL DEFAULT 0,
    low_confidence  INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (release_id, issue_code)
);
CREATE INDEX IF NOT EXISTS idx_pil_code ON {table}(issue_code);
CREATE INDEX IF NOT EXISTS idx_pil_release ON {table}(release_id);
CREATE INDEX IF NOT EXISTS idx_pil_primary ON {table}(release_id, is_primary);
"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true")
    args = ap.parse_args()

    if not DB.exists():
        print(f"ERROR: {DB} not found", file=sys.stderr)
        sys.exit(1)

    con = sqlite3.connect(DB)
    con.execute("PRAGMA journal_mode=WAL")

    print("Fitting logistic-regression classifier on LDA activity descriptions "
          "(~5-6 min)...")
    clf = PressTopicClassifier.fit(con)
    print(f"  {len(clf.codes)} codes with profiles")
    low_conf_codes = {c for c in clf.codes if clf.is_low_confidence(c)}
    if low_conf_codes:
        print(f"  low-confidence codes (< training-volume floor): {sorted(low_conf_codes)}")

    print(f"Building {TABLE}...")
    for stmt in build_ddl(TABLE).strip().split(";"):
        stmt = stmt.strip()
        if stmt:
            con.execute(stmt)
    con.commit()

    total_releases = con.execute(
        "SELECT count(*) FROM press_releases WHERE text IS NOT NULL"
    ).fetchone()[0]
    print(f"  Scoring {total_releases:,} press releases against {len(clf.codes)} code profiles...")

    rows_to_insert: list[tuple] = []
    n_scored = 0
    n_labeled_releases = 0

    cursor = con.execute(
        "SELECT release_id, text FROM press_releases WHERE text IS NOT NULL"
    )
    while True:
        batch = cursor.fetchmany(BATCH_SIZE)
        if not batch:
            break
        release_ids = [r[0] for r in batch]
        texts = [r[1] for r in batch]
        probs = clf.score_batch(texts)  # (batch, n_codes)

        for i, release_id in enumerate(release_ids):
            row_probs = probs[i]
            above = [
                (code, float(row_probs[j]))
                for j, code in enumerate(clf.codes)
                if row_probs[j] >= PROBABILITY_THRESHOLD
            ]
            if not above:
                continue
            n_labeled_releases += 1
            primary_code = max(above, key=lambda kv: kv[1])[0]
            for code, prob in above:
                rows_to_insert.append((
                    release_id, code, prob,
                    1 if code == primary_code else 0,
                    1 if code in low_conf_codes else 0,
                ))

        n_scored += len(batch)
        if n_scored % (BATCH_SIZE * 10) == 0:
            print(f"    ...{n_scored:,}/{total_releases:,} scored")

    con.executemany(
        f"INSERT INTO {TABLE} VALUES (?,?,?,?,?)", rows_to_insert
    )
    con.commit()
    print(f"  Inserted {len(rows_to_insert):,} label rows for {n_labeled_releases:,} "
          f"releases ({100*n_labeled_releases/total_releases:.1f}% of scored releases "
          f"got at least one label).")

    if args.validate:
        ok = validate(con)
        con.close()
        sys.exit(0 if ok else 1)

    con.close()


def validate(con: sqlite3.Connection) -> bool:
    """Reconciliation checks for derived_press_issue_labels. Returns True if
    all checks pass. Compares against the old ISSUE_KEYWORDS-era counts
    (hardcoded from the audit in docs/press-issue-classifier.md) so the
    delta this replacement caused is visible, not just
    asserted -- the plan explicitly calls for "report the delta, don't just
    assert" per the INS case's own "verify the fix doesn't over-correct"
    discipline."""
    ok = True

    def check(label, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  [{'PASS' if cond else 'FAIL'}] {label}")

    print("reconciliation:")

    n = con.execute(f"SELECT count(*) FROM {TABLE}").fetchone()[0]
    check("table non-empty", n > 0)

    for row in con.execute(f"""
        SELECT 'rows' AS m, count(*) FROM {TABLE} UNION ALL
        SELECT 'distinct_releases', count(DISTINCT release_id) FROM {TABLE} UNION ALL
        SELECT 'distinct_codes', count(DISTINCT issue_code) FROM {TABLE} UNION ALL
        SELECT 'primary_rows', count(*) FROM {TABLE} WHERE is_primary=1 UNION ALL
        SELECT 'low_confidence_rows', count(*) FROM {TABLE} WHERE low_confidence=1
    """):
        print(f"  {row[0]:<20} {row[1]:,}")

    bad_primary = con.execute(f"""
        SELECT release_id, count(*) FROM {TABLE}
        WHERE is_primary=1 GROUP BY release_id HAVING count(*) > 1
    """).fetchall()
    check("every release has at most one is_primary=1 row", len(bad_primary) == 0)

    bad_prob = con.execute(
        f"SELECT count(*) FROM {TABLE} WHERE probability < {PROBABILITY_THRESHOLD} OR probability > 1"
    ).fetchone()[0]
    check(f"probability always in [{PROBABILITY_THRESHOLD}, 1]", bad_prob == 0)

    # Coverage delta vs. the old ISSUE_KEYWORDS-era counts. These are the
    # audited counts from the session that motivated this replacement
    # (scripts/audit_issue_keyword_recall.py output, 2026-07-02/03) -- NOT
    # re-derived here, since ISSUE_KEYWORDS is being deleted from the
    # codebase as part of this migration. This is a point-in-time
    # comparison, not a live reconciliation.
    OLD_KEYWORD_MATCH_COUNTS = {
        # code: n_press_releases matched by the old LIKE-based ISSUE_KEYWORDS,
        # out of 141,332 total releases (audit_issue_keyword_recall.py /
        # ad hoc corpus-wide counts from this session).
        "INS": 1422,   # known-broken, 23% recall bug
        "TAX": 69917,  # suspected over-broad (49.5% of corpus)
        "IMM": 77122,  # suspected over-broad (54.6% of corpus)
        "ENV": 66466,  # suspected over-broad (47.0% of corpus)
        "HCR": 51678,  # suspected over-broad (36.6% of corpus)
    }
    print("\n--- coverage delta vs. old ISSUE_KEYWORDS map (point-in-time comparison) ---")
    for code, old_n in OLD_KEYWORD_MATCH_COUNTS.items():
        new_n = con.execute(
            f"SELECT count(*) FROM {TABLE} WHERE issue_code=?", (code,)
        ).fetchone()[0]
        direction = "more" if new_n > old_n else "fewer"
        print(f"  {code:5s} old={old_n:,} new={new_n:,} ({direction}, "
              f"{100*(new_n-old_n)/old_n:+.0f}%)")
    print("  (TAX/IMM/ENV/HCR decreasing is the expected, desired direction --")
    print("   these were suspected over-broad in the old keyword map, not a")
    print("   regression here. INS ALSO decreases under this classifier --")
    print("   NOT the naively-expected recall fix. Investigated in depth:")
    print("   most of the old map's INS matches (even the case's own hand-")
    print("   disambiguated BROAD_INS_KEYWORDS) were actually HEALTH insurance")
    print("   mentions the LIKE-matching couldn't distinguish from insurance-")
    print("   as-a-regulated-industry -- the classifier correctly excludes most")
    print("   of those, a real precision win. But isolating to genuinely")
    print("   industry-specific insurance language (flood/property/title/auto),")
    print("   this classifier's recall is real but moderate (~25% in one manual")
    print("   check) -- a known, moderate gap, not a bug. See the domain-")
    print("   mismatch section of docs/press-issue-classifier.md for the")
    print("   full investigation and why LLM-based")
    print("   training augmentation (tried, to close this gap) was abandoned.)")

    print("\n--- per-code row counts (top 15) ---")
    for row in con.execute(f"""
        SELECT issue_code, count(*) AS n
        FROM {TABLE} GROUP BY issue_code ORDER BY n DESC LIMIT 15
    """):
        print(f"  {row[0]:5s} {row[1]:,}")

    return ok


if __name__ == "__main__":
    main()
