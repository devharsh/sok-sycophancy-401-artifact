# Artifact schema

Machine-readable systematization for "SoK: Sycophancy as an Integrity Failure in Human-AI
Decision Systems" (ASIACCS 2027 submission). Regenerate and validate with
`python3 build_artifacts.py` from the repository root; the script exits non-zero if any CSV
drifts from the paper's tables or if any citation key fails to resolve in `references.bib`.

## corpus.csv (62 rows, one per reference)
- key: BibTeX key in references.bib
- year: publication or preprint year
- venue: venue name, or arXiv/PsyArXiv for preprints, or vendor name
- evidence_status: peer-reviewed | preprint | vendor-report
- role: function in the systematization (foundational-audit, survey, benchmark, mechanistic,
  cause-study, theory, consequence-study, user-study, mitigation, foundational-alignment,
  incident-report, incident-analysis; compounds joined with +)
- construct: propositional | social | propositional+social | general | n/a
- elicitation: elicitation paradigm used by the study (n/a for non-empirical work)
- modality: text | image | video | mixed | n/a
- tier: control tier for mitigation-relevant sources (data | training | inference | policy | n/a)

## benchmarks.csv (10 rows) = Table 5 of the paper
benchmark, domain, format, focus, key_result, models, strengths, limitations, ref

## mitigations.csv (14 rows) = Table 6 of the paper
method, tier, effectiveness, cost, applicability, mechanism, tradeoffs, refs (semicolon-separated)

## metrics.csv (9 rows) = Table 7 of the paper
metric, definition, ref

## coverage.csv (6 rows) = Table 4 of the paper
channel; one coverage level per control tier (full | partial | none); then per-tier
semicolon-separated citation keys supporting the coding. "full" requires a published control
directly targeting the channel with reported evaluation; "partial" is partial or degrading
coverage; "none" means no published control was found in the corpus.
