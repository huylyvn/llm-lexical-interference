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

        if not low["parse_ok"] or not high["parse_ok"]:
            raise ValueError(
                f"{pair_id} contains a parsing failure"
            )


def calculate_metrics(pairs):
    total_pairs = len(pairs)

    low_correct = 0
    high_correct = 0

    flips = 0
    harmful_flips = 0
    beneficial_flips = 0

    for pair_id, conditions in pairs.items():
        low = conditions["low_conflict"]
        high = conditions["high_conflict"]

        if low["correct"]:
            low_correct += 1

        if high["correct"]:
            high_correct += 1

        # A flip means the model chose different answer letters
        if low["parsed_answer"] != high["parsed_answer"]:
            flips += 1

            # Correct in low conflict, wrong in high conflict
            if low["correct"] and not high["correct"]:
                harmful_flips += 1

            # Wrong in low conflict, correct in high conflict
            elif not low["correct"] and high["correct"]:
                beneficial_flips += 1

    low_accuracy = low_correct / total_pairs
    high_accuracy = high_correct / total_pairs

    paired_accuracy_difference = high_accuracy - low_accuracy

    flip_rate = flips / total_pairs
    harmful_flip_rate = harmful_flips / total_pairs
    beneficial_flip_rate = beneficial_flips / total_pairs

    return {
        "total_pairs": total_pairs,
        "low_correct": low_correct,
        "high_correct": high_correct,
        "low_accuracy": low_accuracy,
        "high_accuracy": high_accuracy,
        "paired_accuracy_difference": paired_accuracy_difference,
        "flips": flips,
        "flip_rate": flip_rate,
        "harmful_flips": harmful_flips,
        "harmful_flip_rate": harmful_flip_rate,
        "beneficial_flips": beneficial_flips,
        "beneficial_flip_rate": beneficial_flip_rate,
    }


def print_metrics(metrics):
    print()
    print("BASELINE RESULTS")
    print("----------------")

    print(
        f"Low-conflict accuracy: "
        f"{metrics['low_correct']}/{metrics['total_pairs']} "
        f"({metrics['low_accuracy']:.1%})"
    )

    print(
        f"High-conflict accuracy: "
        f"{metrics['high_correct']}/{metrics['total_pairs']} "
        f"({metrics['high_accuracy']:.1%})"
    )

    print(
        f"Paired accuracy difference: "
        f"{metrics['paired_accuracy_difference']:.1%}"
    )

    print(
        f"Answer flips: "
        f"{metrics['flips']}/{metrics['total_pairs']} "
        f"({metrics['flip_rate']:.1%})"
    )

    print(
        f"Harmful flips: "
        f"{metrics['harmful_flips']}/{metrics['total_pairs']} "
        f"({metrics['harmful_flip_rate']:.1%})"
    )

    print(
        f"Beneficial flips: "
        f"{metrics['beneficial_flips']}/{metrics['total_pairs']} "
        f"({metrics['beneficial_flip_rate']:.1%})"
    )


def main():
    results = load_results("results/run_003.jsonl")

    print(f"Loaded {len(results)} result(s)")

    pairs = group_by_pair(results)

    print(f"Found {len(pairs)} matched pair(s)")

    validate_pairs(pairs)

    print("Result validation passed")

    metrics = calculate_metrics(pairs)

    print_metrics(metrics)


if __name__ == "__main__":
    main()