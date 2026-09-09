import json

from dotenv import load_dotenv
from anthropic import Anthropic
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


def main():
    items = load_items("data/benchmark.jsonl")

    print(f"Loaded {len(items)} item(s)")

    item = items[0]
    prompt = build_prompt(item)

    print()
    print("PROMPT SENT TO MODEL:")
    print("---------------------")
    print(prompt)


if __name__ == "__main__":
    main()