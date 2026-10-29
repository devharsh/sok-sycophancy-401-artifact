# Anonymous artifact for ASIACCS 2027 submission #401

SoK: Sycophancy as an Integrity Failure in Human-AI Decision Systems

This repository accompanies the author response. It has two parts. Both run with Python 3 and
the standard library only.

## systematization/ (as submitted)

The machine-readable systematization described in the paper's Open Science appendix, unchanged
from the submitted version:

- `artifacts/corpus.csv`: the 62 coded sources; `benchmarks.csv` (10 benchmarks),
  `mitigations.csv` (14 mitigation methods), `metrics.csv` (9 metrics), `coverage.csv`
  (6 rows); column definitions in `artifacts/schema.md`.
- `build_artifacts.py`: regenerates every CSV and validates it against the paper's tables and
  bibliography; exits non-zero on any drift.
- `paper.latex`, `sections/`, `references.bib`: the anonymized paper source the validator runs
  against.

Run: `python3 systematization/build_artifacts.py`

## search/ (added during the response period)

The reproducible database search requested by Reviewers A and B, with every screening decision
and the instrument coding used in the response. `search/SEARCH_PROTOCOL.md` states the query,
endpoint, retrieval time, cutoff, screening criteria, and coding definitions.

Run: `python3 search/reproduce_counts.py` (recomputes every count quoted in the response).
