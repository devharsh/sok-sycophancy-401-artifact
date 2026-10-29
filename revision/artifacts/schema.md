# Artifact schema

Machine-readable systematization for "SoK: Sycophancy as an Integrity Failure in Human-AI
Decision Systems" (ASIACCS 2027 submission, revised). Regenerate and validate with
`python3 build_artifacts.py` from the repository root; the script exits non-zero if any CSV
drifts from the paper's tables or claims, or if any citation key fails to resolve in
`references.bib` or is missing from the appendix tables.

## corpus.csv (128 rows, one per reference)
- key: BibTeX key in references.bib
- year: publication or preprint year (arXiv sources: year of the first version)
- venue: venue name, or arXiv/PsyArXiv for preprints, or vendor name
- evidence_status: peer-reviewed | preprint | vendor-report
- role: function in the systematization (foundational-audit, survey, survey-position, benchmark,
  mechanistic, cause-study, theory, formal-analysis, consequence-study, user-study, mitigation,
  attack-analysis, foundational-alignment, incident-report, incident-analysis; compounds joined
  with +)
- construct: propositional | social | propositional+social | general | n/a; for instruments added
  by the search, reference-R | reference-C | reference-N | reference-E (see benchmarks.csv)
- elicitation: elicitation paradigm (single-turn | multi-turn | other; n/a for non-empirical work)
- modality: text | image | video | audio | agentic | mixed | n/a
- tier: control tier for mitigation-relevant sources (data | training | inference | policy | n/a)

## benchmarks.csv (44 rows) = Table 5 of the paper (Table 2 groups the same rows)
instrument, reference_type (R correctness label | C counterfactual stance shift with evidence held
fixed | N human or clinical norm | E evidence-calibrated update), year, modality, domain_format,
models, headline_result (as reported by the source), refs

## mitigations.csv (38 rows) = Table 6 of the paper
method, tier, access (B black-box | W white-box activations or logits | T weight training),
effect_verbatim (the source's own words), rerun_by_other_group (Y or --), grade, internal_conflict
(yes when the source's own numbers conflict), refs (semicolon-separated).
Grade: A meets all of (i) at least two model families, (ii) at least two task domains, (iii)
multi-turn or held-out testing; B two; C one; D none; U a method proposed against sycophancy whose
source reports no sycophancy measurement; n/a for the two policy rows. Per-row evidence with
quotes, models, domains, and page locations is in search/mitigation_grades.jsonl at the
root of the artifact repository.

## metrics.csv (9 rows) = Table 7 of the paper
metric, definition, ref

## coverage.csv (7 rows) = Table 4 of the paper
channel; one coverage level per control tier (full | partial | none | out-of-scope); then per-tier
semicolon-separated citation keys supporting the coding. "full" requires a published control
directly targeting the channel with reported evaluation; "partial" is partial, degrading, or
proxy-only coverage; "none" means no published control was found; "out-of-scope" marks embedded
instructions (indirect prompt injection), whose defenses lie outside the corpus.
