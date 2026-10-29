#!/usr/bin/env python3
"""Recompute every count quoted in the rebuttal from the CSV files in this folder.

Usage: python3 reproduce_counts.py
"""
import collections
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CUTOFF = "2026-08-20"


def load(name):
    with open(os.path.join(HERE, name), newline="") as f:
        return list(csv.DictReader(f))


def year(arxiv_id):
    return 2000 + int(arxiv_id[:2])


records = load("datacite_records.csv")
pre = [r for r in records if r["registered"] and r["registered"] <= CUTOFF]
print(f"Identification: {len(records)} records retrieved; {len(pre)} registered by {CUTOFF}")

screen = load("screening_decisions.csv")
assert {r["arxiv"] for r in screen} == {r["arxiv"] for r in pre}, "screening set != cutoff set"
kept = [r for r in screen if r["include"] == "Y"]
dropped = [r for r in screen if r["include"] != "Y"]
print(f"Screening: {len(kept)} retained, {len(dropped)} excluded "
      f"{dict(collections.Counter(r['exclude_code'] for r in dropped))}")
print(f"  retained marked uncertain (co-equal subject): {sum(r['uncertain'] == 'True' for r in kept)}")
print(f"  retained by arXiv year: {sorted(collections.Counter(year(r['arxiv']) for r in kept).items())}")
print(f"  roles: {dict(collections.Counter(r['role'] for r in kept))}")
titles = {r["arxiv"]: r["title"] for r in records}
concept = [r["arxiv"] for r in kept if r["role"] == "SURVEY" and r["in_corpus"] != "True"
           and "sycophan" in titles[r["arxiv"]].lower()]
print(f"  SURVEY-role papers outside the submitted corpus whose titles name sycophancy: "
      f"{len(concept)} {concept}")

recall = load("recall_check.csv")
hit = [r for r in recall if r["returned_by_query"] == "True"]
print(f"Recall check: query returns {len(hit)} of {len(recall)} arXiv papers in the submitted corpus")
print("  not returned:", ", ".join(r["bibkey"] for r in recall if r["returned_by_query"] != "True"))

inst = load("instruments_coded.csv")
print(f"Dedicated instruments: {len(inst)}; reference types {dict(collections.Counter(r['paradigm'] for r in inst))}")
in_tables = [r for r in inst if r["in_paper_tables"] == "True"]
omitted = [r for r in inst if r["in_paper_tables"] != "True"]
print(f"  covered by the paper's benchmark tables: {len(in_tables)}; omitted: {len(omitted)} "
      f"by year {dict(sorted(collections.Counter(r['year'] for r in omitted).items()))}")
print("  omitted before 2026:", ", ".join(r["instrument"] for r in omitted if int(r["year"]) < 2026))
for y in ("2025", "2026"):
    ys = [r for r in inst if r["year"] == y]
    non_r = sum(r["paradigm"] != "R" for r in ys)
    print(f"  {y}: {len(ys)} instruments, non-correctness share {non_r}/{len(ys)} = {non_r / len(ys):.0%}")
agentic = sorted(r["arxiv"] for r in inst if "agentic" in r["modality"])
print(f"  agentic or memory instruments: {len(agentic)}, earliest arXiv id {agentic[0]}")

mit = load("mitigations_absent_from_table6.csv")
print(f"Sycophancy-specific mitigations absent from Table 6: {len(mit)}")
