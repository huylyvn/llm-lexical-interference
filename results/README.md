## Benchmark v1 results

Benchmark v1 contains 25 matched semantic problems (50 total cases), with one `low_conflict` and one `high_conflict` condition per pair.

All runs below used:

* Model: `claude-haiku-4-5-20251001`
* Dataset: benchmark v1
* `max_tokens=256`
* Same parser and scoring pipeline

### Baseline prompt v0

Two unchanged baseline runs were used to check whether observed behavior was stable.

#### run_008

* Fully scorable matched pairs: 24/25
* Low-conflict accuracy: 24/24 (100%)
* High-conflict accuracy: 23/24 (95.8%)
* Harmful flips: 1/24
* Strict output-format compliance: 41/50 (82%)
* Parsing failures: 2/50

#### run_009

* Fully scorable matched pairs: 24/25
* Paired low-conflict accuracy: 24/24 (100%)
* Paired high-conflict accuracy: 23/24 (95.8%)
* Harmful flips: 1/24
* Strict output-format compliance: 42/50 (84%)
* Parsing failures: 1/50

### pair_024 — repeated baseline harmful flip

The same harmful flip occurred in both v0 baseline runs.

* Low conflict: D (correct)
* High conflict: B (incorrect)

The high-conflict distractor was a true statement strongly associating Ben with Cedar and the invoice mismatch, while the question required tracking who requested the correction, which was Asha.

The repeated result is consistent with an item-level lexical-interference effect involving actor/action binding. However, it is based on one synthetic matched pair and should not be generalized to overall model behavior.

## Prompt intervention v1

Prompt v1 added a general instruction to:

* answer based on meaning rather than lexical overlap;
* avoid selecting an option merely because it repeats wording from the context;
* check that the selected option directly answers the question.

The benchmark, model, token budget, parser, and scoring logic were otherwise unchanged.

### First v1 run

* Fully scorable matched pairs: 23/25
* Paired accuracy difference: 0.0 percentage points
* Harmful flips: 0/23
* Strict output-format compliance: 25/50 (50%)
* Parsing failures: 2/50

For pair_024:

* Low conflict: D (correct)
* High conflict: D (correct)

### run_011 — v1 replication

* Fully scorable matched pairs: 23/25
* Paired accuracy difference: 0.0 percentage points
* Harmful flips: 0/23
* Strict output-format compliance: 25/50 (50%)
* Parsing failures: 3/50

For pair_024:

* Low conflict: D (correct)
* High conflict: D (correct)

## Narrow interpretation

Across two v0 baseline runs, pair_024 produced the same correct-to-incorrect flip under increased lexical conflict.

Across two v1 intervention runs, that pair remained correct in both conditions and no harmful flips were observed among fully scorable matched pairs.

This provides preliminary evidence that the explicit semantic/distractor-checking prompt may reduce the observed lexical-interference failure on this benchmark.

However, the intervention also produced a reproducible drop in strict one-letter output-format compliance:

* v0: 82–84%
* v1: 50%

The v1 prompt therefore appears to involve a possible tradeoff between semantic robustness and output-protocol reliability under the current 256-token output limit.

These results come from a small synthetic benchmark and a single hosted model. They should be interpreted as pilot evidence rather than a general claim about LLM robustness.

## Evaluation limitations

Some verbose responses were truncated before producing an explicit final answer and were treated as unscorable rather than semantic errors.

The intervention runs also exposed a parser edge case where an explicit answer letter may appear before a verbose explanation but fail conservative parsing. Parser improvements should be applied generically and retrospectively to all saved runs rather than tailored to individual examples.
