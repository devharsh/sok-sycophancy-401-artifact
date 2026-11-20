#!/usr/bin/env python3
"""Regenerate and validate the machine-readable systematization artifacts (revised version).

Single source of truth for artifacts/*.csv. Regenerates every CSV, then validates:
  1. corpus.csv covers exactly the reference list, in both directions;
  2. every citation key used in any artifact resolves in references.bib and is cited in the
     corresponding LaTeX table;
  3. row counts and category counts match the claims in the paper (128 sources; 44 instruments,
     26 R, 8 C, 8 N, 2 E; 36 graded mitigations, 8 A, 12 B, 8 C, 6 D, 2 U, 4 re-run, 8 flagged;
     9 metrics; 7 coverage rows);
  4. headline numbers in the artifacts appear verbatim in the LaTeX sources.
Exits non-zero on any drift. Run after ANY edit to the tables in sections/ or to references.bib.
"""
import collections, csv, os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
NON_CORPUS_KEYS = {"trivedi2026sycophancyartifact"}
ART = os.path.join(ROOT, "artifacts")
os.makedirs(ART, exist_ok=True)

# ---------------------------------------------------------------- corpus coding
# fields: key, year, venue, evidence_status, role, construct, elicitation, modality, tier
CORPUS = [
 ('sharma2023understanding', 2023, 'arXiv', 'preprint', 'foundational-audit', 'propositional+social', 'single-turn-challenge', 'text', 'n/a'),
 ('perez2023discovering', 2023, 'ACL Findings', 'peer-reviewed', 'foundational-audit', 'propositional', 'model-written-evals', 'text', 'n/a'),
 ('malmqvist2024sycophancy', 2024, 'arXiv', 'preprint', 'survey', 'general', 'n/a', 'text', 'n/a'),
 ('ye2026taxonomy', 2026, 'arXiv', 'preprint', 'survey-taxonomy', 'general', 'n/a', 'text', 'n/a'),
 ('casper2023rlhf', 2023, 'arXiv', 'preprint', 'survey', 'general', 'n/a', 'n/a', 'n/a'),
 ('ji2023hallucination', 2023, 'ACM Computing Surveys', 'peer-reviewed', 'survey-adjacent', 'n/a', 'n/a', 'text', 'n/a'),
 ('fanous2025syceval', 2025, 'AIES', 'peer-reviewed', 'benchmark', 'propositional', 'single-turn-rebuttal', 'text', 'n/a'),
 ('celebi2025parrot', 2025, 'arXiv', 'preprint', 'benchmark', 'propositional', 'authority-framing', 'text', 'n/a'),
 ('hong2025sycon', 2025, 'EMNLP Findings', 'peer-reviewed', 'benchmark', 'propositional+social', 'multi-turn-pressure', 'text', 'n/a'),
 ('cheng2026elephant', 2026, 'ICLR', 'peer-reviewed', 'benchmark', 'social', 'advice-query', 'text', 'n/a'),
 ('rahman2025pendulum', 2025, 'arXiv', 'preprint', 'benchmark', 'propositional', 'visual-conflict', 'image', 'n/a'),
 ('zhou2025flattery', 2025, 'arXiv', 'preprint', 'benchmark', 'propositional', 'visual-conflict', 'video', 'n/a'),
 ('zhang2025pressure', 2025, 'arXiv', 'preprint', 'benchmark+mitigation', 'propositional', 'false-premise+multi-turn', 'text', 'training'),
 ('botas2026aedi', 2026, 'arXiv', 'preprint', 'benchmark-metric', 'propositional', 'attitude-gradient', 'text', 'policy'),
 ('pandey2025beacon', 2025, 'arXiv', 'preprint', 'benchmark', 'propositional', 'single-turn-decomposed', 'text', 'n/a'),
 ('auyeung2025psychogenic', 2025, 'arXiv', 'preprint', 'benchmark', 'social', 'delusional-persona', 'text', 'n/a'),
 ('kasneci2026edu_safety', 2026, 'arXiv', 'preprint', 'benchmark-position', 'propositional+social', 'authority+face-saving', 'text', 'policy'),
 ('lin2022truthfulqa', 2022, 'ACL', 'peer-reviewed', 'benchmark-adjacent', 'n/a', 'imitative-falsehood', 'text', 'n/a'),
 ('genadi2026linear', 2026, 'EACL', 'peer-reviewed', 'mechanistic', 'propositional', 'probe-steering', 'text', 'inference'),
 ('wang2026truthoverridden', 2026, 'AAAI', 'peer-reviewed', 'mechanistic', 'propositional', 'opinion-statement', 'text', 'n/a'),
 ('vennemeyer2025notone', 2025, 'arXiv', 'preprint', 'mechanistic', 'propositional+social', 'activation-analysis', 'text', 'n/a'),
 ('duszenko2026anchors', 2026, 'arXiv', 'preprint', 'mechanistic', 'propositional', 'counterfactual-rollout', 'text', 'inference'),
 ('burns2022latent', 2022, 'arXiv', 'preprint', 'mechanistic-adjacent', 'n/a', 'latent-probe', 'text', 'n/a'),
 ('turpin2023faithful', 2023, 'NeurIPS', 'peer-reviewed', 'mechanistic-adjacent', 'propositional', 'biased-context', 'text', 'n/a'),
 ('feng2026reasoning', 2026, 'arXiv', 'preprint', 'cause-study', 'propositional', 'multi-turn-pressure', 'text', 'n/a'),
 ('ranaldi2023contradict', 2023, 'arXiv', 'preprint', 'cause-study', 'propositional', 'single-turn-challenge', 'text', 'n/a'),
 ('kim2025challenging', 2025, 'EMNLP Findings', 'peer-reviewed', 'cause-study', 'propositional', 'rebuttal-framing', 'text', 'n/a'),
 ('dubois2026askdont', 2026, 'arXiv', 'preprint', 'cause-study+mitigation', 'propositional', 'framing-factorial', 'text', 'inference'),
 ('ibrahim2026warm', 2026, 'Nature', 'peer-reviewed', 'cause-study', 'propositional+social', 'persona-finetune', 'text', 'data'),
 ('shapira2026rlhf', 2026, 'arXiv', 'preprint', 'theory', 'propositional', 'formal-analysis', 'n/a', 'training'),
 ('skalse2022reward', 2022, 'NeurIPS', 'peer-reviewed', 'theory', 'n/a', 'formal-analysis', 'n/a', 'n/a'),
 ('wang2026pch', 2026, 'arXiv', 'preprint', 'theory', 'general', 'formal-analysis', 'n/a', 'n/a'),
 ('amodei2016concrete', 2016, 'arXiv', 'preprint', 'theory', 'n/a', 'n/a', 'n/a', 'n/a'),
 ('denison2024subterfuge', 2024, 'arXiv', 'preprint', 'theory-safety', 'general', 'curriculum-generalization', 'text', 'n/a'),
 ('liu2026rewards', 2026, 'arXiv', 'preprint', 'consequence-study', 'general', 'rl-sandbox', 'text', 'n/a'),
 ('cheng2025prosocial', 2026, 'Science', 'peer-reviewed', 'consequence-study', 'social', 'live-interaction', 'text', 'n/a'),
 ('batista2026rational', 2026, 'arXiv', 'preprint', 'consequence-study', 'propositional', 'rule-discovery-task', 'text', 'n/a'),
 ('bo2026saboteurs', 2026, 'CHI', 'peer-reviewed', 'consequence-study', 'propositional', 'task-assistant', 'text', 'n/a'),
 ('rathje2025attitude', 2025, 'PsyArXiv', 'preprint', 'consequence-study', 'propositional+social', 'political-conversation', 'text', 'n/a'),
 ('li2026sycophancy_decisions', 2026, 'CHI', 'peer-reviewed', 'consequence-study', 'social', 'decision-task', 'text', 'n/a'),
 ('chen2025helpfulness', 2025, 'npj Digital Medicine', 'peer-reviewed', 'consequence-study', 'propositional', 'illogical-request', 'text', 'training'),
 ('turner2026programmed', 2026, 'AI and Ethics', 'peer-reviewed', 'ethics-theory', 'general', 'n/a', 'n/a', 'policy'),
 ('lipinska2024ontological', 2025, 'arXiv', 'preprint', 'theory-clinical', 'social', 'n/a', 'text', 'n/a'),
 ('noshin2026reddit', 2026, 'Canadian AI (PMLR 318)', 'peer-reviewed', 'user-study', 'social', 'forum-corpus', 'text', 'n/a'),
 ('sun2026friendly', 2026, 'CHI', 'peer-reviewed', 'user-study', 'social', 'stance-adaptation', 'text', 'n/a'),
 ('wei2023synthetic', 2023, 'arXiv', 'preprint', 'mitigation', 'propositional', 'synthetic-data', 'text', 'data'),
 ('wang2024synthetic', 2024, 'arXiv', 'preprint', 'mitigation', 'propositional', 'synthetic-data', 'text', 'data'),
 ('chen2024pinpoint', 2024, 'ICML', 'peer-reviewed', 'mitigation', 'propositional', 'head-finetune', 'text', 'training'),
 ('li2025causm', 2025, 'ICLR', 'peer-reviewed', 'mitigation', 'propositional', 'causal-reweighting', 'text', 'training'),
 ('bai2022constitutional', 2022, 'arXiv', 'preprint', 'mitigation', 'general', 'self-critique', 'text', 'training'),
 ('beigi2025smart', 2025, 'EMNLP', 'peer-reviewed', 'mitigation', 'propositional', 'reasoning-trajectories', 'text', 'training'),
 ('panickssery2023steering', 2023, 'arXiv', 'preprint', 'mitigation', 'propositional+social', 'activation-steering', 'text', 'inference'),
 ('kong2024repredit', 2024, 'NeurIPS', 'peer-reviewed', 'mitigation', 'general', 'representation-control', 'text', 'inference'),
 ('hu2025monica', 2025, 'arXiv', 'preprint', 'mitigation', 'propositional', 'step-monitoring', 'text', 'inference'),
 ('christiano2017deep', 2017, 'NeurIPS', 'peer-reviewed', 'foundational-alignment', 'n/a', 'n/a', 'n/a', 'training'),
 ('ziegler2019finetuning', 2019, 'arXiv', 'preprint', 'foundational-alignment', 'n/a', 'n/a', 'text', 'training'),
 ('stiennon2020summarize', 2020, 'NeurIPS', 'peer-reviewed', 'foundational-alignment', 'n/a', 'n/a', 'text', 'training'),
 ('ouyang2022training', 2022, 'NeurIPS', 'peer-reviewed', 'foundational-alignment', 'n/a', 'n/a', 'text', 'training'),
 ('askell2021general', 2021, 'arXiv', 'preprint', 'foundational-alignment', 'n/a', 'n/a', 'text', 'training'),
 ('bai2022rlhf', 2022, 'arXiv', 'preprint', 'foundational-alignment', 'n/a', 'n/a', 'text', 'training'),
 ('openai2025sycophancy', 2025, 'OpenAI (vendor report)', 'vendor-report', 'incident-report', 'social', 'production-rollout', 'text', 'n/a'),
 ('lin2025hiddenprompts', 2025, 'arXiv', 'preprint', 'incident-analysis', 'n/a', 'embedded-instruction', 'text', 'n/a'),
 ('aranya2026grounding', 2026, 'arXiv', 'preprint', 'benchmark', 'reference-R', 'single-turn', 'image', 'n/a'),
 ('atwell2025basil', 2025, 'arXiv', 'preprint', 'benchmark', 'reference-E', 'single-turn', 'text', 'n/a'),
 ('au2026pptbench', 2026, 'arXiv', 'preprint', 'benchmark', 'reference-C', 'multi-turn', 'text', 'n/a'),
 ('batzner2024germanpartiesqa', 2024, 'arXiv', 'preprint', 'benchmark', 'reference-C', 'single-turn', 'text', 'n/a'),
 ('batzner2025claims', 2025, 'arXiv', 'preprint', 'survey-position', 'general', 'n/a', 'n/a', 'n/a'),
 ('bensal2026mist', 2026, 'arXiv', 'preprint', 'benchmark', 'reference-R', 'multi-turn', 'agentic', 'n/a'),
 ('bhalla2026sway', 2026, 'arXiv', 'preprint', 'benchmark', 'reference-C', 'single-turn', 'text', 'n/a'),
 ('bohacek2026cascading', 2026, 'arXiv', 'preprint', 'mitigation', 'propositional', 'n/a', 'text', 'inference'),
 ('chang2026causal', 2026, 'arXiv', 'preprint', 'mitigation', 'propositional', 'n/a', 'text', 'inference'),
 ('chang2026rca', 2026, 'arXiv', 'preprint', 'mitigation', 'propositional', 'n/a', 'text', 'inference'),
 ('chen2026pca', 2026, 'arXiv', 'preprint', 'mitigation', 'propositional', 'n/a', 'text', 'inference'),
 ('christian2026blinding', 2026, 'arXiv', 'preprint', 'mitigation', 'propositional', 'n/a', 'text', 'inference'),
 ('do2026sfs', 2026, 'arXiv', 'preprint', 'benchmark', 'reference-C', 'multi-turn', 'text', 'n/a'),
 ('du2025alignment', 2025, 'arXiv', 'preprint', 'survey-position', 'general', 'n/a', 'n/a', 'n/a'),
 ('dunlap2026feedback', 2026, 'arXiv', 'preprint', 'benchmark', 'reference-R', 'multi-turn', 'text', 'n/a'),
 ('fahad2026codesmell', 2026, 'arXiv', 'preprint', 'mitigation', 'propositional', 'n/a', 'text', 'inference'),
 ('gallego2024rdpo', 2024, 'arXiv', 'preprint', 'mitigation', 'propositional', 'n/a', 'text', 'training'),
 ('germani2026complacent', 2026, 'arXiv', 'preprint', 'survey-position', 'general', 'n/a', 'n/a', 'n/a'),
 ('guo2026muse', 2026, 'arXiv', 'preprint', 'benchmark', 'reference-E', 'multi-turn', 'text', 'n/a'),
 ('han2026implicit', 2026, 'arXiv', 'preprint', 'benchmark', 'reference-N', 'single-turn', 'text', 'n/a'),
 ('hassani2026thesis', 2026, 'arXiv', 'preprint', 'mitigation', 'propositional', 'n/a', 'text', 'inference'),
 ('hong2026visual', 2026, 'arXiv', 'preprint', 'benchmark', 'reference-R', 'single-turn', 'image', 'n/a'),
 ('imran2026rmct', 2026, 'arXiv', 'preprint', 'mitigation', 'propositional', 'n/a', 'text', 'training'),
 ('irpan2025consistency', 2025, 'arXiv', 'preprint', 'mitigation', 'propositional', 'n/a', 'text', 'training'),
 ('jain2026premise', 2026, 'arXiv', 'preprint', 'survey-position', 'general', 'n/a', 'n/a', 'n/a'),
 ('jiang2026cap', 2026, 'arXiv', 'preprint', 'benchmark', 'reference-C', 'single-turn', 'text', 'n/a'),
 ('joy2026medpress', 2026, 'arXiv', 'preprint', 'benchmark', 'reference-N', 'multi-turn', 'text', 'n/a'),
 ('kasprova2026polite', 2026, 'arXiv', 'preprint', 'mitigation', 'propositional', 'n/a', 'text', 'inference'),
 ('kelkar2026persona', 2026, 'arXiv', 'preprint', 'mitigation', 'propositional', 'n/a', 'text', 'inference'),
 ('laban2023flipflop', 2023, 'arXiv', 'preprint', 'benchmark', 'reference-R', 'multi-turn', 'text', 'n/a'),
 ('lai2026tddpo', 2026, 'arXiv', 'preprint', 'mitigation', 'propositional', 'n/a', 'text', 'training'),
 ('lamparth2026reward', 2026, 'arXiv', 'preprint', 'formal-analysis', 'general', 'n/a', 'text', 'training'),
 ('li2024mmsy', 2024, 'arXiv', 'preprint', 'benchmark', 'reference-R', 'single-turn', 'image', 'n/a'),
 ('li2026boundary', 2026, 'arXiv', 'preprint', 'survey-position', 'general', 'n/a', 'n/a', 'n/a'),
 ('li2026flowsteer', 2026, 'arXiv', 'preprint', 'attack-analysis', 'propositional', 'crafted-prompt', 'agentic', 'n/a'),
 ('liu2025truthdecay', 2025, 'arXiv', 'preprint', 'benchmark', 'reference-R', 'multi-turn', 'text', 'n/a'),
 ('liu2026cormrag', 2026, 'arXiv', 'preprint', 'mitigation', 'propositional', 'n/a', 'text', 'inference'),
 ('mao2026pasb', 2026, 'arXiv', 'preprint', 'benchmark', 'reference-R', 'multi-turn', 'agentic', 'n/a'),
 ('mohsin2026pressure', 2026, 'arXiv', 'preprint', 'mitigation', 'propositional', 'n/a', 'text', 'training'),
 ('nogueira2026llmbias', 2026, 'arXiv', 'preprint', 'benchmark', 'reference-C', 'multi-turn', 'text', 'n/a'),
 ('noshin2026bensyc', 2026, 'arXiv', 'preprint', 'benchmark', 'reference-N', 'single-turn', 'text', 'n/a'),
 ('obrien2026neurons', 2026, 'arXiv', 'preprint', 'mitigation', 'propositional', 'n/a', 'text', 'training'),
 ('papadatos2024linear', 2024, 'arXiv', 'preprint', 'mitigation', 'propositional', 'n/a', 'text', 'inference'),
 ('peng2026sycoeval', 2026, 'arXiv', 'preprint', 'benchmark', 'reference-N', 'multi-turn', 'text', 'n/a'),
 ('petrov2025brokenmath', 2025, 'arXiv', 'preprint', 'benchmark', 'reference-R', 'single-turn', 'text', 'n/a'),
 ('pi2025srt', 2025, 'arXiv', 'preprint', 'mitigation', 'propositional', 'n/a', 'image', 'training'),
 ('ravishankara2025fvarag', 2025, 'arXiv', 'preprint', 'mitigation', 'propositional', 'n/a', 'text', 'inference'),
 ('rehani2026scale', 2026, 'arXiv', 'preprint', 'benchmark', 'reference-N', 'single-turn', 'text', 'n/a'),
 ('ryan2026durable', 2026, 'arXiv', 'preprint', 'mitigation', 'propositional', 'n/a', 'text', 'inference'),
 ('shah2026agreeable', 2026, 'arXiv', 'preprint', 'benchmark', 'reference-R', 'single-turn', 'text', 'n/a'),
 ('shah2026silicon', 2026, 'arXiv', 'preprint', 'mitigation', 'propositional', 'n/a', 'text', 'inference'),
 ('shah2026sycophantasy', 2026, 'arXiv', 'preprint', 'benchmark', 'reference-R', 'single-turn', 'image', 'n/a'),
 ('shi2026deception', 2026, 'arXiv', 'preprint', 'survey-position', 'general', 'n/a', 'n/a', 'n/a'),
 ('tan2025duetpd', 2025, 'arXiv', 'preprint', 'benchmark', 'reference-R', 'multi-turn', 'text', 'n/a'),
 ('tang2026gasvideo', 2026, 'arXiv', 'preprint', 'benchmark', 'reference-R', 'multi-turn', 'video', 'n/a'),
 ('vennemeyer2026praise', 2026, 'arXiv', 'preprint', 'benchmark', 'reference-N', 'single-turn', 'text', 'n/a'),
 ('vishwarupe2026pluralistic', 2026, 'arXiv', 'preprint', 'survey-position', 'general', 'n/a', 'n/a', 'n/a'),
 ('wang2026dual', 2026, 'arXiv', 'preprint', 'mitigation', 'propositional', 'n/a', 'text', 'training'),
 ('waqas2025acc', 2025, 'arXiv', 'preprint', 'benchmark', 'reference-R', 'multi-turn', 'agentic', 'n/a'),
 ('xiang2026memsyco', 2026, 'arXiv', 'preprint', 'benchmark', 'reference-R', 'single-turn', 'agentic', 'n/a'),
 ('xiao2026medstress', 2026, 'arXiv', 'preprint', 'benchmark', 'reference-R', 'multi-turn', 'text', 'n/a'),
 ('xu2025viper', 2025, 'arXiv', 'preprint', 'mitigation', 'propositional', 'n/a', 'image', 'inference'),
 ('yao2026syaudio', 2026, 'arXiv', 'preprint', 'benchmark', 'reference-R', 'single-turn', 'audio', 'n/a'),
 ('yuan2025echobench', 2025, 'arXiv', 'preprint', 'benchmark', 'reference-R', 'single-turn', 'image', 'n/a'),
 ('zhao2024itsm', 2024, 'arXiv', 'preprint', 'mitigation', 'propositional', 'n/a', 'image', 'inference'),
 ('zhao2026price', 2026, 'arXiv', 'preprint', 'benchmark', 'reference-R', 'single-turn', 'agentic', 'n/a'),
]

# ------------------------------------------------- dedicated instruments (Table 5, Table 2)
# fields: instrument, reference_type, year, modality, domain_format, models, headline, refs
BENCHMARKS = [
 ('FlipFlop', 'R', '2023', 'Text, MT', 'Seven classification tasks', '10 LLMs', 'Answers flip 46% of the time on average; accuracy falls 17%', 'laban2023flipflop'),
 ('MM-SY', 'R', '2024', 'Image, MT', 'Visual QA, ten task types', '10 VLMs', 'LLaVA-1.5 sycophancy rate 94.6%', 'li2024mmsy'),
 ('SycEval', 'R', '2025', 'Text, MT', 'Math and medical QA', '3 LLMs', 'Sycophantic in 58.19% of cases (43.52% progressive, 14.66% regressive); persistence 78.5%', 'fanous2025syceval'),
 ('TRUTH DECAY', 'R', '2025', 'Text, MT', 'Multiple choice, 7 follow-ups', '3 LLMs', 'Accuracy drops of up to 47% under multi-turn pressure', 'liu2025truthdecay'),
 ('VISE', 'R', '2025', 'Video', 'Video QA', 'Video-LLMs', 'Video-LLMs align with misleading input that contradicts the video', 'zhou2025flattery'),
 ('Pressure-Tune', 'R', '2025', 'Text, MT', 'Scientific QA', 'Open LLMs', 'Degradation driven more by alignment strategy than by model size', 'zhang2025pressure'),
 ('DuET-PD', 'R', '2025', 'Text, MT', 'Knowledge and safety MCQ', '9 LLMs', 'GPT-4o keeps 27.32% MMLU-Pro accuracy under sustained misleading persuasion', 'tan2025duetpd'),
 ('EchoBench', 'R', '2025', 'Image', 'Medical VQA, biased prompts', '24 LVLMs', 'Best proprietary model 45.98% sycophancy; GPT-4.1 59.15%; many medical models above 95%', 'yuan2025echobench'),
 ('BrokenMath', 'R', '2025', 'Text', 'Competition theorem proving', '10 LLMs', 'Best model (GPT-5) sycophantic 29% of the time', 'petrov2025brokenmath'),
 ('Beacon', 'R', '2025', 'Text', 'Mixed, single turn', 'Several LLMs', 'Decomposes position, verbosity, and validation sub-biases', 'pandey2025beacon'),
 ('PARROT', 'R', '2025', 'Text', 'MMLU-style, 13 domains', '22 LLMs', 'Authority follow rate 4% (GPT-5) to 94% (Qwen 2.5-1.5B)', 'celebi2025parrot'),
 ('A-CC', 'R', '2025', 'Agentic, MT', 'Multi-turn tool calling', '11 LLMs', 'Compliance with user assertions 36.3% (confident) vs. 27.7% (hedged); with tool-sourced assertions 27.8%', 'waqas2025acc'),
 ('PENDULUM', 'R', '2025', 'Image', 'Visual QA, six domains', 'MLLMs', 'Pronounced susceptibility on about 2,000 human-curated pairs', 'rahman2025pendulum'),
 ('Feedback indices', 'R', '2026', 'Text, MT', 'Physics MCQ, rebuttals', '8 OpenAI models', 'Sycophancy index 0.97 (GPT-4.1-nano), lower for newer reasoning models', 'dunlap2026feedback'),
 ('SYAUDIO', 'R', '2026', 'Audio', 'Audio MCQ, four domains', '5 ALMs', 'Mean flip share 41.51 with audio question and cue vs. 14.05 text only', 'yao2026syaudio'),
 ('Tri-layer diagnostic', 'R', '2026', 'Image', 'VQA under blind, noise, conflict', '9 VLMs', '72.9% of samples show visual sycophancy (split beliefs)', 'hong2026visual'),
 ('L-VASE, CCS', 'R', '2026', 'Image', 'Medical VQA', '6 VLMs', 'No model reaches a clinical safety index above 0.35', 'aranya2026grounding'),
 ('Agreeable personas', 'R', '2026', 'Text', '275 personas, 33 topics', '13 small LLMs', 'Agreeableness predicts sycophancy in 9 of 13 models (r up to 0.87)', 'shah2026agreeable'),
 ('GasVideo-1000', 'R', '2026', 'Video, MT', 'Video QA, negation gaslighting', '6 Vid-LLMs', 'Gemini-3-Pro accuracy falls 37.70 points', 'tang2026gasvideo'),
 ('SycoPhantasy', 'R', '2026', 'Image', 'Image-text alignment scoring', '6 VLMs', 'Unjustified high scores 22.3% (450M) vs. 6.0% (7B)', 'shah2026sycophantasy'),
 ('Price of Agreement', 'R', '2026', 'Agentic', 'Financial QA with tools', '8 LLMs', 'Preference injection cuts Gemini-3-Pro accuracy from 0.83 to 0.24', 'zhao2026price'),
 ('EduFrameTrap', 'R', '2026', 'Text', 'Tutoring, six subjects', '2 LLMs', 'Authority and face-saving pressure trigger epistemic retreat', 'kasneci2026edu_safety'),
 ('Med-Stress', 'R', '2026', 'Text, MT', 'Clinical QA, escalating pressure', '9 LLMs', 'GPT-4o: 97.88% initial accuracy but belief stability 41.50', 'xiao2026medstress'),
 ('MIST', 'R', '2026', 'Agentic, MT', 'Memory; science, medical, moral', '5 families', 'Memory raises sycophancy by up to 40% over in-context baselines', 'bensal2026mist'),
 ('MemSyco-Bench', 'R', '2026', 'Agentic', 'Agent memory, five tasks', '2 LLMs, 7 memories', 'Memory raises Qwen3-8B sycophancy from 27.43 to between 44.47 and 64.67', 'xiang2026memsyco'),
 ('PASB', 'R', '2026', 'Agentic, MT', 'Personal agents, 1,600 tasks', '16 models', 'Downstream failure 68.1% when the claim was saved vs. 35.6% when not', 'mao2026pasb'),
 ('GermanPartiesQA', 'C', '2024', 'Text', 'Party positions, personas', '6 LLMs', 'Persona adaptation reflects steerability rather than sycophancy', 'batzner2024germanpartiesqa'),
 ('SYCON', 'C', '2025', 'Text, MT', 'Debate, ethics, presuppositions', '17 LLMs', 'All models eventually flip under sustained pressure', 'hong2025sycon'),
 ('SWAY', 'C', '2026', 'Text', 'Positive vs. negative framing', '6 LLMs', 'Sycophancy increases with epistemic commitment', 'bhalla2026sway'),
 ('PPT-Bench', 'C', '2026', 'Text, MT', 'Epistemic attack, three layers', '5 LLMs', 'Pressure types yield separable inconsistency patterns', 'au2026pptbench'),
 ('llm-bias-bench', 'C', '2026', 'Text, MT', 'Contested topics, five turns', '13 LLMs', 'Median sycophancy 50% under direct questioning vs. 79% in debate', 'nogueira2026llmbias'),
 ('Selective flip score', 'C', '2026', 'Text, MT', 'Simulated students', '7 LLMs', 'Near-zero selective flipping: models abandon simulated misconceptions', 'do2026sfs'),
 ('AEDI (Pander Score)', 'C', '2026', 'Text', 'Mixed propositions', '8 models', 'Continuous deference score over 16,000 prompts', 'botas2026aedi'),
 ('CAP', 'C', '2026', 'Text', 'Advice, 12 domains', '17 LLMs', 'Preference-induced stance reversal from 5% to 56%', 'jiang2026cap'),
 ('ELEPHANT', 'N', '2025', 'Text', 'Interpersonal advice', '11 LLMs', 'Face preserved 45 points more than humans; either side of a moral conflict affirmed in 48%', 'cheng2026elephant'),
 ('PsychMachine', 'N', '2025', 'Text, MT', 'Psychiatric simulation', '8 LLMs', 'Delusion confirmation 0.91, harm enablement 0.69 (0 to 1 scale)', 'auyeung2025psychogenic'),
 ('SycoEval-EM', 'N', '2026', 'Text, MT', 'Emergency medicine, agents', '19 LLMs', 'Acquiescence to guideline-discordant requests from 0% to 100%', 'peng2026sycoeval'),
 ('Social sycophancy scale', 'N', '2026', 'Text', 'Rated conversations', 'N = 877 raters', 'Validated three-factor measure without ground truth', 'rehani2026scale'),
 ('DESG benchmark', 'N', '2026', 'Text', 'Mental-health dialogue audit', '1,500 windows', 'Implicit sycophancy detection improves 0.0488 macro-F1 over baselines', 'han2026implicit'),
 ('Sycophantic praise', 'N', '2026', 'Text', 'Reasoning vs. social prompts', '4 LLMs', 'Praise 41.9% in moral reasoning vs. 1.3% in economics (one model)', 'vennemeyer2026praise'),
 ('BenSyc', 'N', '2026', 'Text', 'Regional social posts', '15+ LLMs', 'Best detection 61.8 macro-F1', 'noshin2026bensyc'),
 ('MedPRESS', 'N', '2026', 'Text, MT', 'Patient-pressure dialogues', '20 LLMs', '86.8% of five-turn conversations contain an unsafe agreement', 'joy2026medpress'),
 ('BASIL', 'E', '2025', 'Text', 'Uncertain forecasting, norms', '6 LLMs', 'Separates sycophantic belief shifts from Bayesian updating', 'atwell2025basil'),
 ('MUSE', 'E', '2026', 'Text, MT', 'Medical, economics MCQ', '7 LLMs', 'Under uncertainty, switch rates rise 10.6 to 27.5 points above pure sycophancy', 'guo2026muse'),
]

# ------------------------------------------------------------ mitigations (Table 6)
# fields: method, tier, access, effect_verbatim, rerun_by_other_group, grade, internal_conflict, refs
MITIGATIONS = [
 ('Synthetic anti-sycophancy data', 'data', 'T', "models tuned with our intervention technique repeat the user's opinion up to 10.0% less often than Flan-PaLM models", 'Y', 'B', 'no', 'wei2023synthetic'),
 ('Supervised pinpoint tuning', 'training', 'T', 'the answer truthfulness of Llama-2-13B increases from 18.89% to 84.06% (+65.17%) after SFT, while SPT achieves 86.72% (+67.83%)', 'Y', 'A', 'no', 'chen2024pinpoint'),
 ('CAUSM head reweighting', 'training', 'T', 'our CAUSM demonstrates the highest average truthfulness by 47.15% on TruthfulQA across different preference prompts', '--', 'A', 'yes', 'li2025causm'),
 ('SMART (tree search plus RL)', 'training', 'T', 'achieving gains ranging from +31.9% to +46.4% over the sycophantic run', '--', 'A', 'no', 'beigi2025smart'),
 ('Reward decomposition (GRPO)', 'training', 'T', 'reducing answer-priming sycophancy by up to 17 points on SycophancyEval despite the absence of such pressure forms during training', '--', 'A', 'yes', 'mohsin2026pressure'),
 ('Lagrangian DPO (Dignified Peer)', 'training', 'T', 'Lag-DPO achieves the lowest Sycophancy Rate (0.542) [...] reducing servility by 33 points over Vanilla', '--', 'A', 'no', 'wang2026dual'),
 ('Pressure-Tune', 'training', 'T', 'the SRR of Llama3-8B increases from 0.69% to 60.33%, while Qwen2.5-3B improves from 29.61% to 85.33%', '--', 'B', 'no', 'zhang2025pressure'),
 ('Consistency training (BCT, ACT)', 'training', 'T', 'While BCT and ACT reduce sycophancy equally well, BCT does better at jailbreak reduction', 'Y', 'B', 'no', 'irpan2025consistency'),
 ('Rate-matching consistency training', 'training', 'T', 'achieving reductions in bias-following comparable to a standard consistency-training baseline on held-out bias types', '--', 'B', 'no', 'imran2026rmct'),
 ('Holistic DPO', 'training', 'T', "improving Llama-3.1-8B-Instruct's accuracy under misleading persuasion in safety contexts from 4.21% to 76.54%", '--', 'B', 'no', 'tan2025duetpd'),
 ('Token-difference DPO', 'training', 'T', 'TD-DPO achieved the best performance across all three base models, yielding an average NSR of 90.90%', '--', 'B', 'no', 'lai2026tddpo'),
 ('Sycophantic reflective tuning', 'training', 'T', 'a significant reduction in sycophantic behavior toward misleading instructions, without resulting in excessive stubbornness', '--', 'B', 'no', 'pi2025srt'),
 ('Neuron-level fine-tuning', 'training', 'T', 'our method matches or exceeds state-of-the-art performance on four benchmarks (Syco-Bench, NLP, POLI, PHIL)', '--', 'B', 'yes', 'obrien2026neurons'),
 ('Bayesian SFT and DPO', 'training', 'T', 'significant reductions in both sycophancy and Bayesian error associated with our novel fine-tuning methods', '--', 'C', 'yes', 'atwell2025basil'),
 ('Prompting, SFT, DPO for VLMs', 'training', 'T', 'The DPO method demonstrates impressive performance (-89.2 Syc)', '--', 'D', 'no', 'li2024mmsy'),
 ('Refined DPO', 'training', 'T', 'rDPO is shown to be effective in [...] reduced sycophancy', '--', 'D', 'no', 'gallego2024rdpo'),
 ('Third-person perspective prompt', 'inference', 'B', 'adopting a third-person perspective reduces sycophancy by up to 63.8% in debate scenario', '--', 'A', 'no', 'hong2025sycon'),
 ('PCA-guided activation scaling', 'inference', 'W', 'PAS achieves strong monotonicity (Spearman rho = +0.92) and an average shift of 15.4% per direction, compared with 8.7% for the baselines', '--', 'A', 'no', 'chen2026pca'),
 ('Sycophancy priors for agent debate', 'inference', 'B', 'improves final discussion accuracy by an absolute 10.5%', '--', 'A', 'no', 'kasprova2026polite'),
 ('Query neutralizer and decoding', 'inference', 'W', 'this framework effectively mitigates sycophancy across all evaluated models, while maintaining performance on neutral prompts', '--', 'B', 'yes', 'zhao2024itsm'),
 ('MONICA reasoning monitor', 'inference', 'W', 'MONICA achieves top-two performance in 33 out of 48 evaluation metrics', '--', 'B', 'no', 'hu2025monica'),
 ('Silicon Mirror gating', 'inference', 'B', 'Claude Sonnet 4 exhibits 9.6% baseline sycophancy, reduced to 1.4% by the Silicon Mirror', '--', 'B', 'no', 'shah2026silicon'),
 ('Bayesian calibration', 'inference', 'B', 'significantly reduces Bayesian error for both the base and sycophancy cases', '--', 'B', 'no', 'atwell2025basil'),
 ("Ask Don't Tell reframing", 'inference', 'B', 'asking a model to convert non-questions into questions before answering significantly reduces sycophancy', '--', 'C', 'no', 'dubois2026askdont'),
 ('Contrastive Activation Addition', 'inference', 'W', 'the addition/subtraction of the steering vectors increased/decreased the prevalence of the behavior', 'Y', 'C', 'no', 'panickssery2023steering'),
 ('Persona vectors', 'inference', 'W', "about 68% (Gemma) and 98% (Qwen) of CAA's reduction in the sycophancy logit", '--', 'C', 'no', 'kelkar2026persona'),
 ('VIPER prompt (medical VLMs)', 'inference', 'B', 'boosts resistance up to 94.7% without sacrificing baseline diagnostic accuracy', '--', 'C', 'yes', 'xu2025viper'),
 ('Self-blinding', 'inference', 'B', 'exhibit dramatically lower rates of sycophancy', '--', 'C', 'no', 'christian2026blinding'),
 ('Evidence-guided prompts (code)', 'inference', 'B', 'lowering Decision Flip Rates to as low as 12% and False Alignment Rates to as low as 21%', '--', 'C', 'no', 'fahad2026codesmell'),
 ('THESIS-MoE interventions', 'inference', 'W', 'Our conditional interventions removed up to 90% of the belief-induced sycophancy', '--', 'C', 'no', 'hassani2026thesis'),
 ('Probe-penalized reward (best-of-N)', 'inference', 'W', 'optimizing against this surrogate reward function reduces sycophantic behavior in multiple open-source LLMs', '--', 'D', 'no', 'papadatos2024linear'),
 ('Regulated causal anchoring', 'inference', 'B', 'achieving 0.0% sycophancy while accepting 88% of valid hints', '--', 'D', 'yes', 'chang2026rca;chang2026causal'),
 ('Adversarial arbitration', 'inference', 'B', 'DeWin achieving 48.5% accuracy (single model 18.5%)', '--', 'D', 'yes', 'ryan2026durable'),
 ('Cascading linear features', 'inference', 'W', 'achieves a sycophancy score of 0.33, effectively matching the performance of the strongest system prompting baseline (0.33)', '--', 'D', 'no', 'bohacek2026cascading'),
 ('FVA-RAG retrieval', 'inference', 'B', 'Reports TruthfulQA accuracy (80.05%) with no user belief injected', '--', 'U', 'no', 'ravishankara2025fvarag'),
 ('CoRM-RAG evidence critic', 'inference', 'B', 'Reports accuracy under biased queries, not a sycophancy measure', '--', 'U', 'no', 'liu2026cormrag'),
 ('Pander Score (AEDI) tracking', 'policy', 'B', 'Continuous deference score proposed for longitudinal tracking', '--', 'n/a', 'no', 'botas2026aedi'),
 ('Robustness testing in model cards', 'policy', 'B', 'SycEval and SYCON proposed as release criteria', '--', 'n/a', 'no', 'fanous2025syceval;hong2025sycon'),
]

# ---------------------------------------------------------------- metrics (Table 7)
METRICS = [
 ('sycophancy rate', "share of responses agreeing with the user's (often wrong) position", 'fanous2025syceval'),
 ('progressive rate', 'share of capitulations landing on correct answers', 'fanous2025syceval'),
 ('regressive rate', 'share of capitulations landing on incorrect answers', 'fanous2025syceval'),
 ('Turn of Flip (ToF)', 'turns until the model first changes stance under pressure', 'hong2025sycon'),
 ('Number of Flips', 'stance changes across a conversation', 'hong2025sycon'),
 ('AEDI score', 'continuous sensitivity of expressed support to user attitude', 'botas2026aedi'),
 ('authority follow rate', 'share of cases following an incorrect authority figure', 'celebi2025parrot'),
 ('misleading resistance', "accuracy maintained under a user's false premise", 'zhang2025pressure'),
 ('rubric score', 'judge-rated facets (agreement, flattery, validation)', 'dubois2026askdont'),
]

# ---------------------------------------------------------------- coverage (Table 4)
# levels: full, partial, none, out-of-scope
COVERAGE = [
 ('single-turn framing (assertion, certainty)', 'full', 'full', 'partial', 'partial', 'wei2023synthetic;chen2024pinpoint;li2025causm', 'dubois2026askdont;panickssery2023steering;genadi2026linear', 'fanous2025syceval;botas2026aedi', 'noshin2026reddit'),
 ('multi-turn pressure', 'partial', 'partial', 'partial', 'none', 'zhang2025pressure;beigi2025smart;tan2025duetpd', 'hong2025sycon;hu2025monica;shah2026silicon', 'hong2025sycon', 'bo2026saboteurs'),
 ('authority, emotion framing', 'partial', 'partial', 'partial', 'none', 'ibrahim2026warm;kasneci2026edu_safety', 'dubois2026askdont;xu2025viper', 'celebi2025parrot', 'noshin2026reddit'),
 ('premise, document assertions', 'none', 'partial', 'partial', 'partial', '', 'ravishankara2025fvarag;liu2026cormrag', 'waqas2025acc', 'turpin2023faithful;zhang2025pressure'),
 ('embedded instructions', 'out-of-scope', 'out-of-scope', 'out-of-scope', 'out-of-scope', '', '', '', 'lin2025hiddenprompts'),
 ('covert, subtle forms', 'partial', 'none', 'partial', 'none', 'imran2026rmct', '', 'han2026implicit;hong2026visual', 'sharma2023understanding;ye2026taxonomy'),
 ('post-deployment drift', 'none', 'none', 'partial', 'none', '', '', 'botas2026aedi;shapira2026rlhf', ''),
]


def write_csv(name, header, rows):
    with open(os.path.join(ART, name), "w", newline="") as f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)

def main():
    failures = []
    write_csv("corpus.csv", ["key", "year", "venue", "evidence_status", "role", "construct",
                             "elicitation", "modality", "tier"], CORPUS)
    write_csv("benchmarks.csv", ["instrument", "reference_type", "year", "modality", "domain_format",
                                 "models", "headline_result", "refs"], BENCHMARKS)
    write_csv("mitigations.csv", ["method", "tier", "access", "effect_verbatim", "rerun_by_other_group",
                                  "grade", "internal_conflict", "refs"], MITIGATIONS)
    write_csv("metrics.csv", ["metric", "definition", "ref"], METRICS)
    write_csv("coverage.csv", ["channel", "data_training", "inference", "monitor_govern",
                               "human_oversight", "cites_data_training", "cites_inference",
                               "cites_monitor_govern", "cites_oversight"], COVERAGE)

    # 1. corpus equals the bibliography
    bib = open(os.path.join(ROOT, "references.bib")).read()
    # The artifact's own entry is cited in the Open Science appendix but is not a corpus source.
    bibkeys = set(re.findall(r"@\w+\{([^,\s]+),", bib)) - NON_CORPUS_KEYS
    corpuskeys = [r[0] for r in CORPUS]
    if len(set(corpuskeys)) != len(corpuskeys):
        failures.append("duplicate keys in corpus")
    if set(corpuskeys) != bibkeys:
        failures.append(f"corpus/bib mismatch: only-in-corpus={sorted(set(corpuskeys) - bibkeys)} "
                        f"only-in-bib={sorted(bibkeys - set(corpuskeys))}")

    # 2. keys resolve and appear in the LaTeX tables
    split = lambda s: [k for k in s.split(";") if k]
    appendix = open(os.path.join(ROOT, "sections", "12-appendix.latex")).read()
    cited = set(k.strip() for grp in re.findall(r"\\cite[pt]?\{([^}]*)\}", appendix) for k in grp.split(","))
    used = set()
    for r in BENCHMARKS + MITIGATIONS: used |= set(split(r[-1]))
    used |= {r[-1] for r in METRICS}
    for r in COVERAGE:
        for cell in r[5:]: used |= set(split(cell))
    if used - bibkeys:
        failures.append(f"citation keys not in references.bib: {sorted(used - bibkeys)}")
    table_keys = set()
    for r in BENCHMARKS + MITIGATIONS: table_keys |= set(split(r[-1]))
    if table_keys - cited:
        failures.append(f"artifact rows not cited in the appendix tables: {sorted(table_keys - cited)}")

    # 3. counts match the paper's claims
    def expect(name, got, want):
        if got != want: failures.append(f"{name}: artifact has {got}, paper claims {want}")
    expect("corpus entries", len(CORPUS), 128)
    expect("dedicated instruments", len(BENCHMARKS), 44)
    expect("instruments by reference type", dict(collections.Counter(r[1] for r in BENCHMARKS)),
           {"R": 26, "C": 8, "N": 8, "E": 2})
    graded = [r for r in MITIGATIONS if r[1] != "policy"]
    expect("graded mitigations", len(graded), 36)
    expect("grade distribution", dict(sorted(collections.Counter(r[5] for r in graded).items())),
           {"A": 8, "B": 12, "C": 8, "D": 6, "U": 2})
    expect("methods re-run by another group", sum(r[4] == "Y" for r in MITIGATIONS), 4)
    expect("rows with internal conflicts", sum(r[6] == "yes" for r in MITIGATIONS), 8)
    expect("metrics", len(METRICS), 9)
    expect("coverage rows", len(COVERAGE), 7)

    # 4. headline numbers appear verbatim in the LaTeX sources
    tex = "".join(open(os.path.join(ROOT, "sections", fn)).read()
                  for fn in sorted(os.listdir(os.path.join(ROOT, "sections"))) if fn.endswith(".latex"))
    tex += open(os.path.join(ROOT, "paper.latex")).read()
    for num in ["58.19", "78.5", "77.2", "79.8", "43.52", "14.66", "63.8", "1,302", "16,000", "0.91",
                "0.69", "84.6", "0.74", "4.78", "49.29", "2{,}405", "3,600", "140,416", "7.97", "9.96",
                "168", "67.83", "8.57", "81.4", "423", "277", "146", "94.6", "98.6", "27.8", "36.3",
                "10.5", "4 of 15", "13 of 26"]:
        if num not in tex:
            failures.append(f"number {num} in artifacts but not found in LaTeX sources")

    if failures:
        print("ARTIFACT VALIDATION FAILED"); [print(" -", f) for f in failures]; sys.exit(1)
    print(f"OK: artifacts regenerated and validated ({len(CORPUS)} corpus, {len(BENCHMARKS)} instruments, "
          f"{len(MITIGATIONS)} mitigation rows, {len(METRICS)} metrics, {len(COVERAGE)} coverage rows; "
          f"all keys resolve and are cited)")

if __name__ == "__main__":
    main()
