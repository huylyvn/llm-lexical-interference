# Lexical Interference in LLM Multiple-Choice Reasoning

A small controlled evaluation of whether increasing lexical overlap with an incorrect answer changes an LLM's response when the underlying semantic problem is held approximately constant.

## Research question

> How much does increasing lexical overlap with an incorrect option change an LLM's answer when the underlying semantic problem is held approximately constant?

This is a pilot evaluation of one hosted language model on a small synthetic benchmark. It is not intended to establish a general property of LLM behavior.

## Experimental design

The benchmark uses **matched perturbation pairs**.

Each underlying semantic problem appears in two conditions:

* `low_conflict`: the incorrect options have relatively limited lexical overlap with the relevant context;
* `high_conflict`: an incorrect option is modified to have stronger lexical overlap with relevant context while the underlying semantic problem and correct answer are held approximately constant.

The final benchmark contains:

* 25 matched semantic problems;
* 2 conditions per pair;
* 50 total benchmark cases.

The correct answer remains fixed within each matched pair.

This design allows the analysis to focus on whether changing lexical conflict changes the model's answer rather than simply comparing unrelated easy and difficult questions.

## Model

All reported runs used:

```text
claude-haiku-4-5-20251001
```

Provider:

```text
Anthropic
```

The model is accessed through a hosted API. Exact token-for-token reproduction is therefore not guaranteed.

The goal of this repository is **reproducibility of the experimental procedure**: a reviewer should be able to inspect and rerun the benchmark, prompt construction, parsing, scoring, and paired analysis.

## Prompt conditions

The benchmark version and prompt version are separate.

### Benchmark v1

`data/benchmark_v1.jsonl`

This is the fixed 25-pair benchmark used for the reported baseline and intervention runs.

### Baseline prompt v0

The baseline prompt presents the context, question, and four answer choices and asks the model to return one answer letter.

### Intervention prompt v1

The intervention keeps the benchmark unchanged but adds explicit instructions to:

* answer based on meaning rather than lexical overlap;
* avoid choosing an option merely because it repeats wording from the context;
* check that the selected option directly answers the question.

The intervention therefore changes the **prompt**, not the benchmark.

## Evaluation pipeline

The experiment follows this pipeline:

```text
benchmark
    ↓
data validation
    ↓
prompt construction
    ↓
hosted-model inference
    ↓
raw output
    ↓
conservative parsing
    ↓
scoring
    ↓
matched-pair analysis
```

Before model calls are made, the benchmark is validated for matched-pair structure and answer consistency.

Raw model output is preserved locally so parsing and scoring behavior can be inspected afterward.

## Metrics

The main paired metrics are:

### Paired accuracy difference

Difference in correctness between the low-conflict and high-conflict conditions among fully scorable matched pairs.

### Answer flip rate

How often the selected answer changes between the two conditions.

### Harmful flip

A pair where:

```text
low conflict = correct
high conflict = incorrect
```

### Beneficial flip

A pair where:

```text
low conflict = incorrect
high conflict = correct
```

### Protocol compliance

Whether the model follows the requested output format.

Protocol compliance is reported separately from semantic correctness.

A response that cannot be conservatively parsed is treated as unscorable rather than automatically classified as semantically wrong.

## Main result

Two unchanged runs using **baseline prompt v0** reproduced the same harmful flip on one matched pair, `pair_024`.

In that pair:

```text
low conflict:  D — correct
high conflict: B — incorrect
```

The high-conflict distractor was factually true and strongly overlapped with the context, but it referred to the person who identified a document problem rather than the person who requested its correction.

The same failure appeared in both baseline runs.

Two subsequent runs using **intervention prompt v1** produced:

```text
low conflict:  D — correct
high conflict: D — correct
```

for the same pair, with no harmful flips among the fully scorable matched pairs in either intervention run.

However, the intervention also produced a substantial and reproducible protocol regression:

| Prompt                 | Strict one-letter output compliance |
| ---------------------- | ----------------------------------: |
| Baseline prompt v0     |                              82–84% |
| Intervention prompt v1 |                                 50% |

The narrow conclusion is therefore:

> On this small synthetic benchmark, explicit semantic/distractor-checking instructions appeared to remove one reproduced lexical-interference failure, but they also substantially worsened strict output-format compliance.

This does **not** establish a general improvement in semantic robustness.

See [`results/README.md`](results/README.md) for run-level results, the complete `pair_024` case study, and detailed interpretation.

## Repository structure

```text
llm-lexical-interference/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   └── benchmark_v1.jsonl
├── results/
│   └── README.md
└── src/
    ├── run_eval.py
    ├── validate_data.py
    └── analyze_results.py
```

### `data/benchmark_v1.jsonl`

The frozen benchmark used for the reported experiment.

### `src/validate_data.py`

Validates matched-pair structure and benchmark consistency.

### `src/run_eval.py`

Loads the benchmark, validates it, constructs the selected prompt version, calls the hosted model, conservatively parses the response, scores it, and saves local run results.

### `src/analyze_results.py`

Groups results into matched pairs and calculates paired behavioral metrics and protocol-compliance information.

### `results/README.md`

Public summary of the reported experimental runs and important failure cases.

Raw result JSONL files are retained locally and are not tracked by Git by default.

## Reproducing the procedure

### 1. Clone the repository

```powershell
git clone <repository-url>
cd llm-lexical-interference
```

### 2. Create a Python environment

The reported development environment used:

```text
Python 3.13.1
```

For example:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure the Anthropic API key

Create a local `.env` file:

```text
ANTHROPIC_API_KEY=your_api_key_here
```

`.env` is excluded from Git and should never be committed.

### 5. Select the prompt condition

`src/run_eval.py` currently keeps the experiment configuration intentionally explicit in the source.

Set:

```python
PROMPT_VERSION = "v0"
```

for the baseline prompt, or:

```python
PROMPT_VERSION = "v1"
```

for the semantic/distractor-checking intervention.

Before running, also use a new local result filename rather than appending to an existing historical run.

### 6. Run the evaluation

```powershell
python src/run_eval.py
```

The runner:

1. loads `data/benchmark_v1.jsonl`;
2. validates the benchmark;
3. constructs the selected prompt;
4. calls the model;
5. preserves the raw response;
6. parses the answer;
7. scores it;
8. saves the result locally.

The validation stage runs before API inference, so benchmark-validation errors stop the experiment before model calls are made.

### 7. Analyze a saved run

```powershell
python src/analyze_results.py
```

The analysis reports matched-pair metrics including accuracy, answer flips, harmful flips, beneficial flips, and protocol-related behavior.

The source currently favors transparent, concrete experiment code over a more abstract configuration framework.

## Parsing policy

The parser is intentionally conservative.

It accepts clear answer forms but does not attempt to recover an answer from arbitrary verbose text merely to increase the apparent score.

This matters because the intervention prompt produced more instruction-violating verbose responses than the baseline prompt.

Changing the parser after observing those responses could alter the measurement itself.

Any future parser modification should therefore be:

* defined generically;
* justified independently of a preferred result;
* applied retrospectively to all saved runs.

The parser was not modified for the results reported in this repository.

## Limitations

### Small benchmark

The benchmark contains only 25 synthetic matched problems.

It is suitable for inspecting controlled behavioral changes but not for estimating general LLM performance.

### One model

All reported runs use one hosted model.

The results do not establish whether the same behavior occurs in other models.

### One central reproduced failure

The strongest qualitative result is based on one matched pair, `pair_024`.

Replication across two baseline runs makes that observation more credible as a property of this specific experiment, but it remains item-level evidence.

### Approximate semantic control

Matched variants were manually designed to preserve the underlying semantic problem while changing lexical conflict.

Perfect semantic equivalence cannot be guaranteed.

### Hosted-model variability

The provider may introduce nondeterminism or implementation changes that prevent exact reproduction of historical outputs.

The repository therefore supports reproduction of the **procedure**, not guaranteed reproduction of every response.

### Output-length effects

Some intervention responses became verbose enough to reach the 256-token output limit before producing an explicit final answer.

The experiment does not isolate how much this contributed to the observed protocol-compliance regression.

### Conservative parser

Some responses may contain recoverable information while still being marked unscorable under the conservative parsing policy.

Semantic performance and protocol compliance are therefore kept conceptually separate.

## Security, privacy, and IP

The public benchmark uses synthetic material created for this project.

The repository does not intentionally include:

* student data;
* private messages;
* teaching records;
* proprietary classroom material;
* commercial IELTS/test-bank questions;
* API keys;
* passwords or credentials.

Local secrets are stored in `.env`, which is excluded from Git.

Raw run JSONL files are also ignored by default. Public experimental evidence is summarized in `results/README.md`.

## Project status

The benchmark and reported experimental runs are frozen.

The current work is limited to publication cleanup, reproducibility documentation, and presentation of the existing evidence.

No additional benchmark expansion or post-hoc experiment redesign is required for the reported pilot result.
