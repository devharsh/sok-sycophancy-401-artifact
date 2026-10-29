# Anonymous artifact for ASIACCS 2027 submission #401

SoK: Sycophancy as an Integrity Failure in Human-AI Decision Systems

This repository accompanies the author response and the revision that implements it. It has three
parts. The validators and the count script run with Python 3 and the standard library only;
regenerating the figures also needs matplotlib (Figures 1 to 3) or Node.js (Figure 4).

## systematization/ (as submitted)

The machine-readable systematization described in the submitted paper's Open Science appendix,
unchanged from the submitted version:

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
endpoint, retrieval time, cutoff, screening criteria, and coding definitions. Comparisons with the
paper in this folder (10 instruments in the benchmark tables, 34 omitted, 21 mitigations absent
from Table 6) refer to the submitted version; the revision adds all 34 instruments to Table 5 and
all 21 mitigations to Table 6.

- `mitigation_grades.jsonl`: the full-text grading behind Table 6 of the revision, one record per
  mitigation result (41 records), with the verbatim effect, models, domains, multi-turn and
  held-out evidence, baselines re-run, and page or table locations. Table 6 merges the BASIL
  Bayesian SFT and DPO records, the two MM-SY records, and the two RCA papers into one row each,
  shows grade C0 as D, and omits Constitutional AI and RE-Control, which report no sycophancy
  evaluation (grade U). The 41 records thus yield its 36 graded rows.
- `instrument_facts.jsonl`: model counts and headline results, with verbatim quotes and locations,
  for the 16 instruments whose abstracts give no numbers.

Run: `python3 search/reproduce_counts.py` (recomputes every count quoted in the response).

## revision/ (revised manuscript)

The manuscript revised as promised in the response.

- `paper.pdf`: the revised paper; `diff_vs_submitted.pdf`: the changes marked against the
  submitted version.
- `paper.latex`, `sections/`, `references.bib`: its anonymized source (128 references).
- `artifacts/`: the updated systematization (128 coded sources, 44 instruments by reference type,
  38 mitigation rows of which 36 are graded and 2 are policy controls, 9 metrics, 7 coverage
  rows), defined in `artifacts/schema.md`.
- `build_artifacts.py`: regenerates and validates those CSVs against the revised tables and claims.
- `figures.ipynb`: regenerates Figures 1 to 3; `figures/fig_search_flow.drawio` is the source of
  Figure 4, rendered by `tools/render_drawio.js` (Node.js with Playwright and mxgraph 4.2.2).

Run: `python3 revision/build_artifacts.py`
