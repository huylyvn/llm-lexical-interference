import json

from dotenv import load_dotenv
from anthropic import Anthropic
from validate_data import validate_pairs, print_answer_distribution
import os

load_dotenv()

client = Anthropic()

def load_items(path):
    items = []

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            item = json.loads(line)
            items.append(item)

    return items

def build_prompt(item):
    choices = item["choices"]

    prompt = f"""Read the context and answer the multiple-choice question.

Context:
{item["context"]}

Question:
{item["question"]}

A. {choices["A"]}
B. {choices["B"]}
C. {choices["C"]}
D. {choices["D"]}

Return exactly one letter: A, B, C, or D."""

    return prompt

def call_model(prompt):
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=8,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
    )

    return message.content[0].text

def parse_answer(raw_output):
    cleaned = raw_output.strip().upper()

    if cleaned in {"A", "B", "C", "D"}:
        return cleaned

    return None


def score_answer(parsed_answer, expected_answer):
    if parsed_answer is None:
        return None

    return parsed_answer == expected_answer

def save_result(result, path):
    with open(path, "a", encoding="utf-8") as file:
        file.write(json.dumps(result) + "\n")

def main():
    items = load_items("data/benchmark.jsonl")

    print(f"Loaded {len(items)} item(s)")

    pairs, errors = validate_pairs(items)

    print(f"Found {len(pairs)} matched pair(s)")

    print_answer_distribution(pairs)

    if errors:
        print("\nVALIDATION FAILED")

        for error in errors:
            print(f"- {error}")

        raise ValueError("Benchmark validation failed")

    print("\nVALIDATION PASSED")

    for item in items:
        prompt = build_prompt(item)
        raw_output = call_model(prompt)

        parsed_answer = parse_answer(raw_output)
        correct = score_answer(parsed_answer, item["answer"])

        result = {
            "pair_id": item["pair_id"],
            "condition": item["condition"],
            "expected_answer": item["answer"],
            "raw_output": raw_output,
            "parsed_answer": parsed_answer,
            "parse_ok": parsed_answer is not None,
            "correct": correct,
            "provider": "anthropic",
            "model": "claude-haiku-4-5-20251001",
            "prompt_version": "v0",
        }

        save_result(result, "results/run_003.jsonl")
        
        print()
        print("PROMPT SENT TO MODEL:")
        print("---------------------")
        print(prompt)

        print()
        print("RAW MODEL OUTPUT:")
        print("-----------------")
        print(raw_output)

        print()
        print("PARSED ANSWER:")
        print("--------------")
        print(parsed_answer)

        print()
        print("CORRECT:")
        print("--------")
        print(correct)

if __name__ == "__main__":
    main()