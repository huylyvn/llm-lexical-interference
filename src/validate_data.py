from collections import Counter, defaultdict


def validate_pairs(items):
    pairs = defaultdict(list)
    errors = []

    for item in items:
        pairs[item["pair_id"]].append(item)

    for pair_id, pair_items in pairs.items():
        conditions = [item["condition"] for item in pair_items]

        if (
            len(pair_items) != 2
            or set(conditions) != {"low_conflict", "high_conflict"}
        ):
            errors.append(
                f"{pair_id}: expected one low_conflict and one high_conflict, "
                f"found {conditions}"
            )

        answers = {item["answer"] for item in pair_items}

        if len(answers) != 1:
            errors.append(
                f"{pair_id}: answers differ across conditions: {answers}"
            )

    return pairs, errors


def print_answer_distribution(pairs):
    answers = []

    for pair_items in pairs.values():
        pair_answers = {item["answer"] for item in pair_items}

        if len(pair_answers) == 1:
            answers.append(next(iter(pair_answers)))

    counts = Counter(answers)
    total = len(answers)

    print("\nCorrect-answer distribution by pair:")

    for option in ["A", "B", "C", "D"]:
        count = counts[option]
        percentage = count / total * 100 if total else 0

        print(f"{option}: {count} ({percentage:.1f}%)")