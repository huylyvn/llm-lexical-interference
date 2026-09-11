import json
from collections import defaultdict


def load_results(path):
    results = []

    with open(path, "r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if line.strip():
                try:
                    result = json.loads(line)
                    results.append(result)
                except json.JSONDecodeError as error:
                    raise ValueError(
                        f"Invalid JSON on line {line_number}: {error}"
                    )

    return results


def group_by_pair(results):
    pairs = defaultdict(dict)

    for result in results:
        pair_id = result["pair_id"]
        condition = result["condition"]

        if condition in pairs[pair_id]:
            raise ValueError(
                f"{pair_id} has more than one {condition} result"
            )

        pairs[pair_id][condition] = result

    return pairs


def validate_pairs(pairs):
    expected_conditions = {"low_conflict", "high_conflict"}

    for pair_id, conditions in pairs.items():

        if set(conditions.keys()) != expected_conditions:
            raise ValueError(
                f"{pair_id} does not contain exactly one "
                f"low_conflict and one high_conflict result"
            )

        low = conditions["low_conflict"]
        high = conditions["high_conflict"]

        if low["expected_answer"] != high["expected_answer"]:
            raise ValueError(
                f"{pair_id} has different expected answers "
                f"across conditions"
            )


def check_strict_format(raw_output):
    cleaned = raw_output.strip().upper()
    return cleaned in {"A", "B", "C", "D"}


def calculate_metrics(pairs):
    total_pairs = len(pairs)
    total_cases = total_pairs * 2

    # Condition-level semantic accuracy.
    # Each condition uses every individually scorable result.
    low_correct = 0
    low_scorable = 0

    high_correct = 0
    high_scorable = 0

    # Paired metrics require BOTH conditions to be scorable.
    scorable_pairs = 0
    paired_low_correct = 0
    paired_high_correct = 0

    flips = 0
    harmful_flips = 0
    beneficial_flips = 0

    parsing_failures = []

    strict_format_ok = 0
    format_violations = []

    for pair_id, conditions in pairs.items():
        low = conditions["low_conflict"]
        high = conditions["high_conflict"]

        # Strict output-format compliance is independent of semantic parsing.
        for condition_name, result in conditions.items():
            if check_strict_format(result["raw_output"]):
                strict_format_ok += 1
            else:
                format_violations.append(
                    (pair_id, condition_name)
                )

        # Low-conflict condition-level accuracy.
        if low["parse_ok"]:
            low_scorable += 1

            if low["correct"]:
                low_correct += 1
        else:
            parsing_failures.append(
                (pair_id, "low_conflict")
            )

        # High-conflict condition-level accuracy.
        if high["parse_ok"]:
            high_scorable += 1

            if high["correct"]:
                high_correct += 1
        else:
            parsing_failures.append(
                (pair_id, "high_conflict")
            )

        # Paired metrics cannot be calculated unless BOTH sides parsed.
        if not low["parse_ok"] or not high["parse_ok"]:
            continue

        scorable_pairs += 1

        if low["correct"]:
            paired_low_correct += 1

        if high["correct"]:
            paired_high_correct += 1

        # A flip means the model chose different answer letters.
        if low["parsed_answer"] != high["parsed_answer"]:
            flips += 1

            # Correct in low conflict, wrong in high conflict.
            if low["correct"] and not high["correct"]:
                harmful_flips += 1

            # Wrong in low conflict, correct in high conflict.
            elif not low["correct"] and high["correct"]:
                beneficial_flips += 1

    # Condition-level semantic accuracies.
    low_accuracy = (
        low_correct / low_scorable
        if low_scorable > 0
        else None
    )

    high_accuracy = (
        high_correct / high_scorable
        if high_scorable > 0
        else None
    )

    # Paired accuracy difference uses the SAME fully scorable pairs
    # on both sides.
    paired_low_accuracy = (
        paired_low_correct / scorable_pairs
        if scorable_pairs > 0
        else None
    )

    paired_high_accuracy = (
        paired_high_correct / scorable_pairs
        if scorable_pairs > 0
        else None
    )

    paired_accuracy_difference = (
        paired_high_accuracy - paired_low_accuracy
        if scorable_pairs > 0
        else None
    )

    flip_rate = (
        flips / scorable_pairs
        if scorable_pairs > 0
        else None
    )

    harmful_flip_rate = (
        harmful_flips / scorable_pairs
        if scorable_pairs > 0
        else None
    )

    beneficial_flip_rate = (
        beneficial_flips / scorable_pairs
        if scorable_pairs > 0
        else None
    )

    strict_format_rate = (
        strict_format_ok / total_cases
        if total_cases > 0
        else None
    )

    parsing_failure_rate = (
        len(parsing_failures) / total_cases
        if total_cases > 0
        else None
    )

    return {
        "total_pairs": total_pairs,
        "total_cases": total_cases,

        "low_correct": low_correct,
        "low_scorable": low_scorable,
        "low_accuracy": low_accuracy,

        "high_correct": high_correct,
        "high_scorable": high_scorable,
        "high_accuracy": high_accuracy,

        "scorable_pairs": scorable_pairs,
        "paired_low_correct": paired_low_correct,
        "paired_high_correct": paired_high_correct,
        "paired_low_accuracy": paired_low_accuracy,
        "paired_high_accuracy": paired_high_accuracy,
        "paired_accuracy_difference": paired_accuracy_difference,

        "flips": flips,
        "flip_rate": flip_rate,
        "harmful_flips": harmful_flips,
        "harmful_flip_rate": harmful_flip_rate,
        "beneficial_flips": beneficial_flips,
        "beneficial_flip_rate": beneficial_flip_rate,

        "parsing_failures": parsing_failures,
        "parsing_failure_rate": parsing_failure_rate,

        "strict_format_ok": strict_format_ok,
        "format_violations": format_violations,
        "strict_format_rate": strict_format_rate,
    }


def format_percentage(value):
    if value is None:
        return "N/A"

    return f"{value:.1%}"


def print_metrics(metrics):
    print()
    print("BASELINE RESULTS")
    print("----------------")

    print(
        f"Low-conflict accuracy: "
        f"{metrics['low_correct']}/{metrics['low_scorable']} "
        f"({format_percentage(metrics['low_accuracy'])})"
    )

    print(
        f"High-conflict accuracy: "
        f"{metrics['high_correct']}/{metrics['high_scorable']} "
        f"({format_percentage(metrics['high_accuracy'])})"
    )

    print(
        f"Fully scorable matched pairs: "
        f"{metrics['scorable_pairs']}/{metrics['total_pairs']}"
    )

    print(
        f"Paired accuracy difference: "
        f"{format_percentage(metrics['paired_accuracy_difference'])}"
    )

    print(
        f"Answer flips: "
        f"{metrics['flips']}/{metrics['scorable_pairs']} "
        f"({format_percentage(metrics['flip_rate'])})"
    )

    print(
        f"Harmful flips: "
        f"{metrics['harmful_flips']}/{metrics['scorable_pairs']} "
        f"({format_percentage(metrics['harmful_flip_rate'])})"
    )

    print(
        f"Beneficial flips: "
        f"{metrics['beneficial_flips']}/{metrics['scorable_pairs']} "
        f"({format_percentage(metrics['beneficial_flip_rate'])})"
    )

    print(
        f"Parsing failures: "
        f"{len(metrics['parsing_failures'])}/{metrics['total_cases']} "
        f"({format_percentage(metrics['parsing_failure_rate'])})"
    )

    if metrics["parsing_failures"]:
        print("Parsing failures:")

        for pair_id, condition in metrics["parsing_failures"]:
            print(f"- {pair_id} / {condition}")

    print(
        f"Strict output-format compliance: "
        f"{metrics['strict_format_ok']}/{metrics['total_cases']} "
        f"({format_percentage(metrics['strict_format_rate'])})"
    )

    if metrics["format_violations"]:
        print("Format violations:")

        for pair_id, condition in metrics["format_violations"]:
            print(f"- {pair_id} / {condition}")


def main():
    results = load_results("results/run_008.jsonl")

    print(f"Loaded {len(results)} result(s)")

    pairs = group_by_pair(results)

    print(f"Found {len(pairs)} matched pair(s)")

    validate_pairs(pairs)

    print("Result validation passed")

    metrics = calculate_metrics(pairs)

    print_metrics(metrics)


if __name__ == "__main__":
    main()