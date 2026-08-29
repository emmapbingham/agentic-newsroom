#!/usr/bin/env python3
"""Reusable classifier: which LDA issue codes is a press release about?

Replaces the hand-curated ISSUE_KEYWORDS LIKE-match map (which had a
confirmed 23%-recall bug on INS, unverified over-matching on IMM/TAX/ENV/
HCR, 9 keyword strings shared across 15 code pairs causing silent
double-counting, and existed as 4 independently-drifting copies across the
codebase -- see docs/press-issue-classifier.md
for the full audit).

Method: the corpus already contains a free, real, correctly-labeled
training set for this exact classification problem --
senate_lobbying_activities.description (keyed by general_issue_code) and
house_activities.description (keyed by issue_area_code) -- both LDA-coded
by the same 79 issue codes the press map targets. This module:

  1. Loads every individual activity description as its own document,
     paired with its code (~1.5M rows).
  2. Fits one sklearn TfidfVectorizer across all of them.
  3. Trains one multinomial LogisticRegression (one-vs-rest under the
     hood for >2 classes), class_weight="balanced" to correct for the
     corpus's heavy code-imbalance (BUD has 183K training examples, MON
     has 322).
  4. Scores a press release with predict_proba -- calibrated,
     cross-code-comparable probabilities.

MODEL HISTORY -- two approaches were tried and rejected before this one,
each for a documented reason (see the plan doc for full detail):

  1. Hand-rolled TF-IDF + cosine-to-centroid (no library). Worked
     reasonably in a first pass but was replaced with scikit-learn per
     editor request, to use a maintained library instead of hand-rolled
     linear algebra.

  2. sklearn TfidfVectorizer + cosine-similarity-to-per-code-centroid
     (the "TF-IDF centroid" approach). Two sub-pitfalls surfaced here:
       a. Fitting the vectorizer on 79 PRE-AGGREGATED per-code text blobs
          (one giant "document" per code) instead of ~1.5M individual
          descriptions degenerates IDF and produces a silently broken
          model (unrelated codes converge on the same top matches).
          Fixed by fitting on individual descriptions instead.
       b. Even fixed, cosine-to-centroid has no single threshold that
          works across codes: a global percentile-of-self-similarity
          threshold either kills recall on precise, narrow-vocabulary
          codes (TAX collapsed to 425 matched releases, down 99% from
          the old keyword map, when hand-checking confirmed genuinely
          on-topic releases were being excluded) or reintroduces false
          positives on codes whose vocabulary overlaps generic
          legislative-process language (ENV/VET matched NIH/WHO/
          gun-safety releases at a looser threshold). A "genericness"
          proxy (centroid's cosine similarity to the corpus-wide mean
          centroid) was tried as an automatic way to set per-code
          percentiles without hand-checking all 75 codes -- it did not
          reliably predict the right direction (VET needed a HIGH
          percentile despite scoring as "distinctive" on the proxy; TAX
          needed a LOW percentile despite scoring as "generic"). This is
          the fundamental limitation of averaging all of a code's
          training examples into one point: it conflates "typical
          example of this code" with "the vocabulary that actually
          distinguishes this code from the other 74," which is precisely
          the information a threshold decision needs.

  3. THIS APPROACH -- multinomial logistic regression, one-vs-rest,
     class_weight="balanced". A discriminative classifier optimizes
     directly for separating each code from the rest (rather than
     averaging examples into a point), so it can learn that a phrase
     like "tax credit" is strong evidence for TAX even when TAX's
     training examples are diluted by generic bill-passage boilerplate.
     Side-by-side comparison against the exact codes that broke the
     centroid approach (INS/TAX/ENV/VET/CPT/PHA) showed sharp, correctly-
     scoped top matches for all six, AND -- critically -- predict_proba
     produces probabilities that are comparable ACROSS codes, so a
     single global probability threshold is viable (unlike cosine
     similarity, which has no natural cross-code scale). See
     build_derived_press_issue_labels.py for the chosen threshold and
     its validation.

Cost: ~5-6 minutes to fit (lbfgs solver, 79 classes, ~1.5M training
examples, ~46K features) -- still local, free, deterministic, and
one-time per rebuild of derived_press_issue_labels; not something a
caller should refit per press release.

Excluded codes: GOV, MIA, SCI, CON -- carried over from the old
ISSUE_KEYWORDS exclusion list. Re-tested GOV in the centroid-approach
phase of this session: even with a real training-text profile, its top
matches are generic legislative-process press (act, bill, federal,
appropriations) sharing only process vocabulary, not GOV-specific
content -- this problem is about the code's own vocabulary being
inherently generic, not an artifact of the centroid method, so it's
expected to persist under logistic regression too and was not re-tested
under the new model. (MIA/SCI/CON were not individually re-tested under
either method; excluded on the same reasoning by analogy.)

Usage as a library:
    from press_topic_classifier import PressTopicClassifier
    clf = PressTopicClassifier.fit(con)
    probs = clf.score(release_text)  # dict[issue_code, float] -- predict_proba
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

DB = Path("db/gain.db")

# Codes excluded because their LDA-activity vocabulary is too generic to
# disambiguate from ordinary political press -- carried over from
# ISSUE_KEYWORDS' exclusion list (build_derived_issue_quarter_volume_press.py
# has the original keyword-era reasoning). GOV re-confirmed under the
# centroid approach; MIA/SCI/CON not individually re-tested, excluded by
# analogy. See module docstring.
EXCLUDED_CODES = {"GOV", "MIA", "SCI", "CON"}

DEFAULT_MIN_DF = 3
DEFAULT_MAX_DF = 0.5

# lbfgs needs >200 iterations to converge at this scale (79 classes, 1.5M
# examples, 46K features) -- 200 produced a ConvergenceWarning; 500 reliably
# converges in ~209 iterations in practice (see plan doc for the timing).
DEFAULT_MAX_ITER = 500

# Codes with fewer than this many activity descriptions get a low-confidence
# flag on their derived_press_issue_labels rows -- not enough training
# signal to trust the classifier's decision boundary for that code the same
# way as a well-populated code.
LOW_TRAIN_VOLUME = 1000


def load_activity_descriptions(con: sqlite3.Connection) -> tuple[list[str], list[str]]:
    """Every individual Senate + House LDA activity description, paired with
    its issue code. Each row is its OWN training example."""
    docs: list[str] = []
    doc_codes: list[str] = []

    for (code, desc) in con.execute(
        "SELECT general_issue_code, description FROM senate_lobbying_activities "
        "WHERE description IS NOT NULL AND length(description) > 5 "
        "AND general_issue_code IS NOT NULL"
    ):
        docs.append(desc)
        doc_codes.append(code)

    for (code, desc) in con.execute(
        "SELECT issue_area_code, description FROM house_activities "
        "WHERE description IS NOT NULL AND length(description) > 5 "
        "AND issue_area_code IS NOT NULL"
    ):
        docs.append(desc)
        doc_codes.append(code)

    return docs, doc_codes


@dataclass
class PressTopicClassifier:
    vectorizer: TfidfVectorizer
    model: LogisticRegression
    codes: list[str]              # clf.model.classes_ order, minus excluded codes
    n_train: dict[str, int]       # code -> number of activity descriptions used

    @classmethod
    def fit(
        cls,
        con: sqlite3.Connection,
        min_df: int = DEFAULT_MIN_DF,
        max_df: float = DEFAULT_MAX_DF,
        max_iter: int = DEFAULT_MAX_ITER,
    ) -> "PressTopicClassifier":
        docs, doc_codes = load_activity_descriptions(con)
        if not docs:
            raise RuntimeError(
                "No LDA activity descriptions found -- is db/gain.db built "
                "with the senate/house stages?"
            )

        # Drop excluded-code training examples before fitting -- the model
        # should never learn a decision boundary for GOV/MIA/SCI/CON, and
        # excluding them here (rather than filtering predictions after
        # fitting) keeps their generic vocabulary from competing for
        # probability mass against the codes we do trust.
        keep = [i for i, c in enumerate(doc_codes) if c not in EXCLUDED_CODES]
        docs = [docs[i] for i in keep]
        doc_codes = [doc_codes[i] for i in keep]

        vectorizer = TfidfVectorizer(
            stop_words="english",
            min_df=min_df,
            max_df=max_df,
            sublinear_tf=True,
        )
        X = vectorizer.fit_transform(docs)
        y = np.array(doc_codes)

        model = LogisticRegression(
            max_iter=max_iter,
            class_weight="balanced",
            C=1.0,
            solver="lbfgs",
        )
        model.fit(X, y)

        n_train = {code: int((y == code).sum()) for code in model.classes_}

        return cls(
            vectorizer=vectorizer,
            model=model,
            codes=list(model.classes_),
            n_train=n_train,
        )

    def score(self, text: str) -> dict[str, float]:
        """predict_proba of `text` against every (non-excluded) code.
        Probabilities are comparable across codes -- callers can apply a
        single global threshold (see build_derived_press_issue_labels.py)."""
        vec = self.vectorizer.transform([text])
        probs = self.model.predict_proba(vec)[0]
        return dict(zip(self.codes, probs.tolist()))

    def score_batch(self, texts: list[str]) -> np.ndarray:
        """Vectorized scoring for many releases at once. Returns
        (n_texts, n_codes) array of predict_proba output; use self.codes
        for column order."""
        matrix = self.vectorizer.transform(texts)
        return self.model.predict_proba(matrix)

    def is_low_confidence(self, code: str) -> bool:
        """True if `code` has too few training examples to trust its
        decision boundary the same way as a well-populated code."""
        return self.n_train.get(code, 0) < LOW_TRAIN_VOLUME


def main() -> None:
    """Smoke test: fit and print a few sanity-check scores."""
    if not DB.exists():
        raise SystemExit(f"{DB} not found")
    con = sqlite3.connect(DB)
    print("Fitting classifier on LDA activity descriptions (this takes ~5-6 min)...")
    clf = PressTopicClassifier.fit(con)
    print(f"  {len(clf.codes)} codes with profiles (excluded: {sorted(EXCLUDED_CODES)})")
    print(f"  vocabulary size: {len(clf.vectorizer.vocabulary_)}")
    n_low_conf = sum(1 for c in clf.codes if clf.is_low_confidence(c))
    print(f"  {n_low_conf} codes flagged low-confidence (< {LOW_TRAIN_VOLUME} training examples)")

    sample = con.execute(
        "SELECT text FROM press_releases WHERE text IS NOT NULL "
        "ORDER BY random() LIMIT 1"
    ).fetchone()[0]
    scores = clf.score(sample)
    top5 = sorted(scores.items(), key=lambda kv: -kv[1])[:5]
    print(f"\nSample release: {sample[:150].strip()}")
    print("Top 5 codes: " + ", ".join(f"{c}({s:.3f})" for c, s in top5))
    con.close()


if __name__ == "__main__":
    main()
