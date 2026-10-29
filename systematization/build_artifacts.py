#!/usr/bin/env python3
"""Regenerate and validate the machine-readable systematization artifacts.

Single source of truth for artifacts/*.csv. Regenerates every CSV, then validates:
  1. every citation key used in any artifact resolves in references.bib;
  2. corpus.csv covers exactly the reference list (62 entries, no more, no fewer);
  3. row counts match the claims and tables in the paper (10 benchmarks, 14 mitigation
     methods, 9 metrics, 6 coverage rows);
  4. headline numbers in the CSVs appear verbatim in the LaTeX sources.
Exits non-zero on any drift, so the Open Science appendix cannot silently overclaim.
Run after ANY edit to the tables in sections/ or to references.bib.
"""
import csv, os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(ROOT, "artifacts")
os.makedirs(ART, exist_ok=True)

# ---------------------------------------------------------------- corpus coding
# fields: key, year, venue, evidence_status, role, construct, elicitation, modality, tier
CORPUS = [
 ("sharma2023understanding",2023,"arXiv","preprint","foundational-audit","propositional+social","single-turn-challenge","text","n/a"),
 ("perez2023discovering",2023,"ACL Findings","peer-reviewed","foundational-audit","propositional","model-written-evals","text","n/a"),
 ("malmqvist2024sycophancy",2024,"arXiv","preprint","survey","general","n/a","text","n/a"),
 ("ye2026taxonomy",2026,"arXiv","preprint","survey-taxonomy","general","n/a","text","n/a"),
 ("casper2023rlhf",2023,"arXiv","preprint","survey","general","n/a","n/a","n/a"),
 ("ji2023hallucination",2023,"ACM Computing Surveys","peer-reviewed","survey-adjacent","n/a","n/a","text","n/a"),
 ("fanous2025syceval",2025,"AIES","peer-reviewed","benchmark","propositional","single-turn-rebuttal","text","n/a"),
 ("celebi2025parrot",2025,"arXiv","preprint","benchmark","propositional","authority-framing","text","n/a"),
 ("hong2025sycon",2025,"EMNLP Findings","peer-reviewed","benchmark","propositional+social","multi-turn-pressure","text","n/a"),
 ("cheng2026elephant",2026,"ICLR","peer-reviewed","benchmark","social","advice-query","text","n/a"),
 ("rahman2025pendulum",2025,"arXiv","preprint","benchmark","propositional","visual-conflict","image","n/a"),
 ("zhou2025flattery",2025,"arXiv","preprint","benchmark","propositional","visual-conflict","video","n/a"),
 ("zhang2025pressure",2025,"arXiv","preprint","benchmark+mitigation","propositional","false-premise+multi-turn","text","training"),
 ("botas2026aedi",2026,"arXiv","preprint","benchmark-metric","propositional","attitude-gradient","text","policy"),
 ("pandey2025beacon",2025,"arXiv","preprint","benchmark","propositional","single-turn-decomposed","text","n/a"),
 ("auyeung2025psychogenic",2025,"arXiv","preprint","benchmark","social","delusional-persona","text","n/a"),
 ("kasneci2026edu_safety",2026,"arXiv","preprint","benchmark-position","propositional+social","authority+face-saving","text","policy"),
 ("lin2022truthfulqa",2022,"ACL","peer-reviewed","benchmark-adjacent","n/a","imitative-falsehood","text","n/a"),
 ("genadi2026linear",2026,"EACL","peer-reviewed","mechanistic","propositional","probe-steering","text","inference"),
 ("wang2026truthoverridden",2026,"AAAI","peer-reviewed","mechanistic","propositional","opinion-statement","text","n/a"),
 ("vennemeyer2025notone",2025,"arXiv","preprint","mechanistic","propositional+social","activation-analysis","text","n/a"),
 ("duszenko2026anchors",2026,"arXiv","preprint","mechanistic","propositional","counterfactual-rollout","text","inference"),
 ("burns2022latent",2022,"arXiv","preprint","mechanistic-adjacent","n/a","latent-probe","text","n/a"),
 ("turpin2023faithful",2023,"NeurIPS","peer-reviewed","mechanistic-adjacent","propositional","biased-context","text","n/a"),
 ("feng2026reasoning",2026,"arXiv","preprint","cause-study","propositional","multi-turn-pressure","text","n/a"),
 ("ranaldi2023contradict",2023,"arXiv","preprint","cause-study","propositional","single-turn-challenge","text","n/a"),
 ("kim2025challenging",2025,"EMNLP Findings","peer-reviewed","cause-study","propositional","rebuttal-framing","text","n/a"),
 ("dubois2026askdont",2026,"arXiv","preprint","cause-study+mitigation","propositional","framing-factorial","text","inference"),
 ("ibrahim2026warm",2026,"Nature","peer-reviewed","cause-study","propositional+social","persona-finetune","text","data"),
 ("shapira2026rlhf",2026,"arXiv","preprint","theory","propositional","formal-analysis","n/a","training"),
 ("skalse2022reward",2022,"NeurIPS","peer-reviewed","theory","n/a","formal-analysis","n/a","n/a"),
 ("wang2026pch",2026,"arXiv","preprint","theory","general","formal-analysis","n/a","n/a"),
 ("amodei2016concrete",2016,"arXiv","preprint","theory","n/a","n/a","n/a","n/a"),
 ("denison2024subterfuge",2024,"arXiv","preprint","theory-safety","general","curriculum-generalization","text","n/a"),
 ("liu2026rewards",2026,"arXiv","preprint","consequence-study","general","rl-sandbox","text","n/a"),
 ("cheng2025prosocial",2026,"Science","peer-reviewed","consequence-study","social","live-interaction","text","n/a"),
 ("batista2026rational",2026,"arXiv","preprint","consequence-study","propositional","rule-discovery-task","text","n/a"),
 ("bo2026saboteurs",2026,"CHI","peer-reviewed","consequence-study","propositional","task-assistant","text","n/a"),
 ("rathje2025attitude",2025,"PsyArXiv","preprint","consequence-study","propositional+social","political-conversation","text","n/a"),
 ("li2026sycophancy_decisions",2026,"CHI","peer-reviewed","consequence-study","social","decision-task","text","n/a"),
 ("chen2025helpfulness",2025,"npj Digital Medicine","peer-reviewed","consequence-study","propositional","illogical-request","text","training"),
 ("turner2026programmed",2026,"AI and Ethics","peer-reviewed","ethics-theory","general","n/a","n/a","policy"),
 ("lipinska2024ontological",2025,"arXiv","preprint","theory-clinical","social","n/a","text","n/a"),
 ("noshin2026reddit",2026,"Canadian AI (PMLR 318)","peer-reviewed","user-study","social","forum-corpus","text","n/a"),
 ("sun2026friendly",2026,"CHI","peer-reviewed","user-study","social","stance-adaptation","text","n/a"),
 ("wei2023synthetic",2023,"arXiv","preprint","mitigation","propositional","synthetic-data","text","data"),
 ("wang2024synthetic",2024,"arXiv","preprint","mitigation","propositional","synthetic-data","text","data"),
 ("chen2024pinpoint",2024,"ICML","peer-reviewed","mitigation","propositional","head-finetune","text","training"),
 ("li2025causm",2025,"ICLR","peer-reviewed","mitigation","propositional","causal-reweighting","text","training"),
 ("bai2022constitutional",2022,"arXiv","preprint","mitigation","general","self-critique","text","training"),
 ("beigi2025smart",2025,"EMNLP","peer-reviewed","mitigation","propositional","reasoning-trajectories","text","training"),
 ("panickssery2023steering",2023,"arXiv","preprint","mitigation","propositional+social","activation-steering","text","inference"),
 ("kong2024repredit",2024,"NeurIPS","peer-reviewed","mitigation","general","representation-control","text","inference"),
 ("hu2025monica",2025,"arXiv","preprint","mitigation","propositional","step-monitoring","text","inference"),
 ("christiano2017deep",2017,"NeurIPS","peer-reviewed","foundational-alignment","n/a","n/a","n/a","training"),
 ("ziegler2019finetuning",2019,"arXiv","preprint","foundational-alignment","n/a","n/a","text","training"),
 ("stiennon2020summarize",2020,"NeurIPS","peer-reviewed","foundational-alignment","n/a","n/a","text","training"),
 ("ouyang2022training",2022,"NeurIPS","peer-reviewed","foundational-alignment","n/a","n/a","text","training"),
 ("askell2021general",2021,"arXiv","preprint","foundational-alignment","n/a","n/a","text","training"),
 ("bai2022rlhf",2022,"arXiv","preprint","foundational-alignment","n/a","n/a","text","training"),
 ("openai2025sycophancy",2025,"OpenAI (vendor report)","vendor-report","incident-report","social","production-rollout","text","n/a"),
 ("lin2025hiddenprompts",2025,"arXiv","preprint","incident-analysis","n/a","embedded-instruction","text","n/a"),
]

# ------------------------------------------------------------- benchmarks (Table 5)
BENCHMARKS = [
 ("SycEval","math, medical QA","single-turn MCQ","false-belief agreement; progressive vs regressive","overall 58.19%; persistence 78.5% (95% CI 77.2-79.8)","ChatGPT-4o; Claude-Sonnet; Gemini-1.5-Pro","peer reviewed (AIES 2025); medical domain","three models; single-turn only","fanous2025syceval"),
 ("SYCON","debate, ethics, factual","multi-turn dialogue","stance-flip speed and frequency under sustained pressure","Turn-of-Flip; Number-of-Flips; all 17 models eventually flip","17 LLMs","largest multi-turn study; reasoning-optimized models included","no visual modality; English only","hong2025sycon"),
 ("ELEPHANT","interpersonal advice","single-turn advice","social sycophancy; face preservation","+45 pp face preservation vs humans; 48% moral-conflict affirmation","11 LLMs + live human study","first social benchmark with human experiment; peer reviewed (ICLR 2026)","subjective ratings; advice domain only","cheng2026elephant"),
 ("PARROT","MMLU-style factual","single-turn MCQ","authority-pressure follow rate","11% (GPT-5) to 94% (Qwen 2.5-1.5B)","22 models","largest model coverage; generational heterogeneity","single-turn; no social-pressure variant","celebi2025parrot"),
 ("PENDULUM","visual QA, six image domains","multimodal","visual sycophancy under conflicting user suggestion","follow rate under visual-text conflict","multimodal LLMs","first multimodal benchmark; ~2,000 human-curated pairs","static images only","rahman2025pendulum"),
 ("VISE","video QA","multimodal (video)","video-LLM alignment with misleading user input","alignment rate against visual evidence","video-LLMs","first video benchmark; multiple question formats","early stage; limited model coverage","zhou2025flattery"),
 ("Pressure-Tune","scientific QA","multi-turn adversarial","resistance to social pressure and false premises","misleading-resistance score; alignment strategy outweighs size","scientific QA models","paired mitigation method","domain-specific","zhang2025pressure"),
 ("AEDI","mixed propositions","single-turn","continuous epistemic-deference sensitivity","AEDI scalar; systematic provider differences","8 models, 16,000 prompts","only continuous scalar; longitudinal tracking","requires domain calibration","botas2026aedi"),
 ("Beacon","mixed","single-turn","decomposed sub-biases: position, verbosity, validation","per-sub-bias scores","multiple LLMs","targeted diagnosis informs mitigation selection","single-turn; synthetic prompts","pandey2025beacon"),
 ("PsychMachine","psychiatric","multi-turn simulation","delusion confirmation and harm enablement","confirmation 0.91; harm enablement 0.69 (0-1)","8 frontier LLMs","only psychiatric-safety benchmark","simulated, not real patients","auyeung2025psychogenic"),
]

# ------------------------------------------------------------- mitigations (Table 6)
MITIGATIONS = [
 ("Synthetic anti-sycophancy data","data","high","low","broad","fine-tuning on synthetic pairs where the sycophantic response is marked incorrect","may degrade general performance if pairs are not domain-representative","wei2023synthetic"),
 ("Supervised Pinpoint Tuning","training","very high","low-med","targeted (<5% of heads)","fine-tunes only sycophancy-driving attention heads; 168M params on Llama-2-13B","requires head identification; less studied beyond Llama","chen2024pinpoint"),
 ("CAUSM","training","high","medium","broad","removes spurious user-preference correlations via causal head reweighting","complex implementation; needs causal graph specification","li2025causm"),
 ("Constitutional AI","training","medium","high","broad","self-critique and revision against explicit honesty principles","slow training loop; principles must be well crafted","bai2022constitutional"),
 ("DPO on contrastive pairs","training","high","medium","broad","maximizes likelihood ratio of truthful over sycophantic completions without an explicit reward model","depends critically on preference-data curation quality","chen2024pinpoint;wang2024synthetic"),
 ("Pressure-Tune","training","high","medium","scientific QA","fine-tunes on adversarial dialogues with rationales that reject misinformation","domain-specific; generalization not demonstrated","zhang2025pressure"),
 ("SMART","training","high","high","reasoning models","uncertainty-aware MCTS generates truthful trajectories under pressure; RL trains on them","computationally expensive; needs reasoning-capable base","beigi2025smart"),
 ("Ask Don't Tell","inference","medium","none","any deployed system","reframing user assertions as questions before answering","weaker under multi-turn pressure; user or system must adopt reframing","dubois2026askdont"),
 ("Third-person perspective prompt","inference","medium","none","multi-turn dialogue","neutral third-person stance instruction; up to 63.8% reduction","degrades with conversation length","hong2025sycon"),
 ("Contrastive Activation Addition","inference","high","low","white-box models","steering vector from mean activation difference of sycophantic vs truthful pairs","needs white-box access; per-domain calibration","panickssery2023steering"),
 ("Representation editing","inference","high","low-med","white-box models","optimal control over hidden-state trajectory via Bellman value function","needs white-box access and value-function training","kong2024repredit"),
 ("MONICA","inference","high","medium","large reasoning models","per-step drift scores; calibrator suppresses sycophantic drift mid-inference","adds latency; validated on three models","hu2025monica"),
 ("AEDI monitoring","policy","ongoing","low","any deployed system","longitudinal deference-score tracking across model versions","periodic re-evaluation; scalar may miss multi-turn dynamics","botas2026aedi"),
 ("Adversarial robustness testing","policy","n/a (eval)","low","high-stakes deployments","SycEval / SYCON as required model-card evaluation criteria","not a direct mitigation; needs community adoption","fanous2025syceval;hong2025sycon"),
]

# ---------------------------------------------------------------- metrics (Table 7)
METRICS = [
 ("sycophancy rate","share of responses agreeing with the user's (often wrong) position","fanous2025syceval"),
 ("progressive rate","share of capitulations landing on correct answers","fanous2025syceval"),
 ("regressive rate","share of capitulations landing on incorrect answers","fanous2025syceval"),
 ("Turn of Flip (ToF)","turns until the model first changes stance under pressure","hong2025sycon"),
 ("Number of Flips","stance changes across a conversation","hong2025sycon"),
 ("AEDI score","continuous sensitivity of expressed support to user attitude","botas2026aedi"),
 ("authority follow rate","share of cases following an incorrect authority figure","celebi2025parrot"),
 ("misleading resistance","accuracy maintained under a user's false premise","zhang2025pressure"),
 ("rubric score","judge-rated facets (agreement, flattery, validation)","dubois2026askdont"),
]

# ---------------------------------------------------------------- coverage (Table 4)
# levels: full = direct published control; partial = partial/degrading; none = no published control
COVERAGE = [
 ("single-turn framing (assertion, certainty)","full","full","partial","partial",
  "wei2023synthetic;chen2024pinpoint;li2025causm","dubois2026askdont;panickssery2023steering;genadi2026linear","fanous2025syceval;botas2026aedi","noshin2026reddit"),
 ("multi-turn pressure","partial","partial","partial","none",
  "zhang2025pressure;beigi2025smart","hong2025sycon;hu2025monica","hong2025sycon","bo2026saboteurs"),
 ("authority, emotion framing","partial","partial","partial","none",
  "ibrahim2026warm;kasneci2026edu_safety","dubois2026askdont","celebi2025parrot","noshin2026reddit"),
 ("premise, embedded instruction","none","none","none","partial",
  "","","","turpin2023faithful;zhang2025pressure"),
 ("covert, subtle forms","none","none","none","none","","","","sharma2023understanding;ye2026taxonomy"),
 ("post-deployment drift","none","none","partial","none","","","botas2026aedi;shapira2026rlhf",""),
]

def write_csv(name, header, rows):
    path = os.path.join(ART, name)
    with open(path, "w", newline="") as f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)
    return path

def main():
    failures = []
    # regenerate
    write_csv("corpus.csv",
        ["key","year","venue","evidence_status","role","construct","elicitation","modality","tier"], CORPUS)
    write_csv("benchmarks.csv",
        ["benchmark","domain","format","focus","key_result","models","strengths","limitations","ref"], BENCHMARKS)
    write_csv("mitigations.csv",
        ["method","tier","effectiveness","cost","applicability","mechanism","tradeoffs","refs"], MITIGATIONS)
    write_csv("metrics.csv", ["metric","definition","ref"], METRICS)
    write_csv("coverage.csv",
        ["channel","data_training","inference","monitor_govern","human_oversight",
         "cites_data_training","cites_inference","cites_monitor_govern","cites_oversight"], COVERAGE)

    # 1-2. bib coverage both directions
    bib = open(os.path.join(ROOT, "references.bib")).read()
    bibkeys = set(re.findall(r"@\w+\{([^,\s]+),", bib))
    corpuskeys = set(r[0] for r in CORPUS)
    if corpuskeys != bibkeys:
        failures.append(f"corpus/bib mismatch: only-in-corpus={sorted(corpuskeys-bibkeys)} "
                        f"only-in-bib={sorted(bibkeys-corpuskeys)}")
    used = set()
    for rows, col in ((BENCHMARKS, -1), (METRICS, -1)):
        used |= {r[col] for r in rows}
    for r in MITIGATIONS:
        used |= set(r[-1].split(";"))
    for r in COVERAGE:
        for cell in r[5:]:
            used |= set(k for k in cell.split(";") if k)
    unknown = used - bibkeys
    if unknown:
        failures.append(f"citation keys not in references.bib: {sorted(unknown)}")

    # 3. counts match the paper's claims
    if len(CORPUS) != 62: failures.append(f"corpus has {len(CORPUS)} entries, paper claims 62")
    if len(BENCHMARKS) != 10: failures.append(f"{len(BENCHMARKS)} benchmarks, paper claims ten")
    if len(MITIGATIONS) != 14: failures.append(f"{len(MITIGATIONS)} mitigation methods, table has 14")
    if len(METRICS) != 9: failures.append(f"{len(METRICS)} metrics, table has 9")
    if len(COVERAGE) != 6: failures.append(f"{len(COVERAGE)} coverage rows, table has 6")

    # 4. headline numbers appear verbatim in the LaTeX sources
    tex = ""
    for fn in sorted(os.listdir(os.path.join(ROOT, "sections"))):
        if fn.endswith(".latex"):
            tex += open(os.path.join(ROOT, "sections", fn)).read()
    tex += open(os.path.join(ROOT, "paper.latex")).read()
    for num in ["58.19", "78.5", "77.2", "79.8", "43.52", "14.66", "63.8", "1,302", "16,000",
                "0.91", "0.69", "84.6", "0.74", "4.78", "49.29", "2{,}405", "3,600", "140,416",
                "7.97", "9.96", "168", "71.84", "67.83", "8.57", "1.59", "81.4"]:
        if num not in tex:
            failures.append(f"number {num} in artifacts but not found in LaTeX sources")

    if failures:
        print("ARTIFACT VALIDATION FAILED"); [print(" -", f) for f in failures]; sys.exit(1)
    print(f"OK: artifacts regenerated and validated "
          f"({len(CORPUS)} corpus, {len(BENCHMARKS)} benchmarks, {len(MITIGATIONS)} mitigations, "
          f"{len(METRICS)} metrics, {len(COVERAGE)} coverage rows; all keys resolve)")

if __name__ == "__main__":
    main()
