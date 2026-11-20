# Artifact: SoK: Sycophancy as an Integrity Failure in Human-AI Decision Systems

Devharsh Trivedi, LaGuardia Community College, City University of New York.

Artifact for the paper accepted at the 22nd ACM ASIA Conference on Computer and Communications
Security (ASIA CCS 2027, Macau, July 12 to 16, 2027). Release v1.0 matches the accepted version.
During review the same repository was shared anonymously; this is its public release.

## Citation

```bibtex
@inproceedings{trivedi2027sycophancy,
  author    = {Devharsh Trivedi},
  title     = {{SoK}: Sycophancy as an Integrity Failure in Human-{AI} Decision Systems},
  booktitle = {Proceedings of the 22nd ACM ASIA Conference on Computer and Communications Security
               (ASIA CCS '27)},
  publisher = {ACM},
  address   = {Macau, China},
  year      = {2027},
  note      = {To appear}
}
```

## Contents

The repository has three parts. The validators and the count script run with Python 3 and the
standard library only; regenerating the figures also needs matplotlib (Figures 1 to 3) or Node.js
(Figure 4).

## systematization/ (as submitted for review)

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

## revision/ (accepted version)

The accepted manuscript: the revision promised in the author response, with the author block
restored and the Open Science appendix pointing to this repository.

- `paper.pdf`: the accepted paper (author version); `diff_vs_submitted.pdf`: the changes marked
  against the submitted version.
- `paper.latex`, `sections/`, `references.bib`: its source (128 corpus references plus the entry
  for this repository). Build with `pdflatex paper.latex; bibtex paper; pdflatex paper.latex;
  pdflatex paper.latex` using acmart v2.19 or later.
- `artifacts/`: the updated systematization (128 coded sources, 44 instruments by reference type,
  38 mitigation rows of which 36 are graded and 2 are policy controls, 9 metrics, 7 coverage
  rows), defined in `artifacts/schema.md`.
- `build_artifacts.py`: regenerates and validates those CSVs against the revised tables and claims.
- `figures.ipynb`: regenerates Figures 1 to 3; `figures/fig_search_flow.drawio` is the source of
  Figure 4, rendered by `tools/render_drawio.js` (Node.js with Playwright and mxgraph 4.2.2).

Run: `python3 revision/build_artifacts.py`

## License

- Code (`*.py`, `figures.ipynb`, `tools/`): MIT License, see `LICENSE`.
- Data and coding (CSV, JSONL and the protocol documents): Creative Commons Attribution 4.0
  International (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/. The DataCite records are
  metadata that DataCite distributes under CC0; quotations from cited papers remain with their
  authors.
- The paper (`paper.pdf`, `diff_vs_submitted.pdf` and the LaTeX sources in `revision/` and
  `systematization/`) is copyright the author and is not covered by these licenses. The version of
  record will appear in the ASIA CCS 2027 proceedings from ACM.
