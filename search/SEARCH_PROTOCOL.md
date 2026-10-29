# Systematic search protocol (rebuttal phase)

This folder documents the reproducible literature search run during the rebuttal for the
submission "SoK: Sycophancy as an Integrity Failure in Human-AI Decision Systems". Every count
quoted in the rebuttal is recomputed from the files here by `reproduce_counts.py`.

## Identification

- Database: DataCite REST API, `https://api.datacite.org/dois`, restricted to client
  `arxiv.content`, the account under which arXiv registers a DOI (10.48550/arXiv.<id>) for every
  arXiv paper. This makes the query independent of any search engine's ranking.
- Query string: `(titles.title:sycophan* OR descriptions.description:sycophan*)`
  (prefix match on titles and abstracts; matches sycophancy, sycophantic, sycophant).
- Retrieved: 2026-10-29T01:47:33Z (UTC). 523 records returned.
- Cutoff: records registered on or before 2026-08-20, the submission date: 423 records.
  The cutoff uses the DataCite `registered` timestamp, so later additions do not change the set.
- Re-run:

```
curl -G "https://api.datacite.org/dois" \
  --data-urlencode "query=(titles.title:sycophan* OR descriptions.description:sycophan*)" \
  --data-urlencode "client-id=arxiv.content" --data-urlencode "page[size]=1000"
```

DataCite metadata reflects the latest arXiv version of each paper, so titles or abstracts can
change after retrieval (for example, one benchmark cited in the paper was later retitled).
`datacite_records.csv` freezes the retrieved metadata.

## Screening (title and abstract)

Inclusion: AI sycophancy is a primary subject. The title names sycophancy, or the abstract states
that measuring, explaining, mitigating, or analyzing consequences of sycophancy is a main
contribution or main finding. Sycophancy means model behavior that conforms to a user's stated or
implied beliefs, preferences, identity, or desired self-image over accuracy or appropriateness.

Exclusion codes: E1 passing mention (listed among failure modes, motivation, or one example);
E2 non-AI sycophancy; E3 other (reason in notes). Records where sycophancy is one of several
co-equal subjects are retained and marked `uncertain=True`.

Roles (one per retained record): BENCH reusable evaluation instrument; MITIG proposes and
evaluates a reduction or control method; MECH internal mechanisms or formal causes; MEAS
measurement without a reusable instrument; HUMAN effects on people; SURVEY survey, position,
taxonomy, or conceptual analysis; OTHER.

Flags (retained records only, Y only when the abstract supports it): F_COVERT covert or implicit
forms; F_DISPLACE suppression of one form shifting into another; F_ADAPTIVE adaptive or
optimizing adversary; F_INJECT third-party content in context (documents, retrieval, tools);
F_MULTITURN multi-turn or sustained pressure; modality.

Process: the first pass was LLM-assisted, run in four parallel batches under this identical
written protocol. Every inclusion, role, and flag carries a verbatim quote from the title or
abstract, checked by script to be an exact substring. The authors then hand-adjudicated
(i) every BENCH record into dedicated versus multi-construct instruments, (ii) every MITIG record
absent from the paper, and (iii) every record flagged F_COVERT, F_DISPLACE, F_ADAPTIVE, or
F_INJECT that bears on a claim in the paper.

## Instrument coding (`instruments_coded.csv`)

Dedicated instrument: sycophancy, or conformity to user pressure, is the primary or co-primary
target. Each is coded by the reference against which a response is judged sycophantic:

- R, correctness-referenced: an external label (answer key, image, video, or audio evidence,
  reference answer) decides capitulation. Only here is the progressive/regressive split defined.
- C, counterfactual stance-sensitivity: output shift between user-stance conditions with the
  evidence held fixed; no correctness label is needed.
- N, normative baseline: a human or professional norm (human advice, clinical guidelines,
  psychometric ratings) decides appropriateness.
- E, evidence-calibrated: models the update that user-supplied evidence warrants, so it can judge
  inputs that mix evidence with pressure.

## Limitations

arXiv-only identification: venue-only works without an arXiv version are covered by the
submitted snowball corpus, not by this query. Coding is at title and abstract level. The first
screening pass was LLM-assisted; decisions that bear on the paper's claims were hand-adjudicated
as described above.

## Files

- `datacite_records.csv`: all 523 retrieved records (title, abstract, registration date).
- `screening_decisions.csv`: the 423 pre-cutoff records with decisions, roles, flags, quotes.
- `instruments_coded.csv`: the 44 dedicated instruments with reference type and year.
- `mitigations_absent_from_table6.csv`: 21 sycophancy-specific mitigations not in the paper.
- `recall_check.csv`: which arXiv papers of the submitted corpus the query returns.
- `reproduce_counts.py`: recomputes every count quoted in the rebuttal.
