import sys
import unittest

sys.path.insert(0, "src")

from validate_data import validate_pairs


class TestValidation(unittest.TestCase):

    def test_valid_pair_passes(self):
        items = [
            {
                "pair_id": "pair_001",
                "condition": "low_conflict",
                "answer": "A",
            },
            {
                "pair_id": "pair_001",
                "condition": "high_conflict",
                "answer": "A",
            },
        ]

        pairs, errors = validate_pairs(items)

        self.assertEqual(len(pairs), 1)
        self.assertEqual(errors, [])

    def test_missing_condition_is_detected(self):
        items = [
            {
                "pair_id": "pair_001",
                "condition": "low_conflict",
                "answer": "A",
            }
        ]

        _, errors = validate_pairs(items)

        self.assertEqual(len(errors), 1)
        self.assertIn(
            "expected one low_conflict and one high_conflict",
            errors[0],
        )

    def test_duplicate_condition_is_detected(self):
        items = [
            {
                "pair_id": "pair_001",
                "condition": "low_conflict",
                "answer": "A",
            },
            {
                "pair_id": "pair_001",
                "condition": "low_conflict",
                "answer": "A",
            },
        ]

        _, errors = validate_pairs(items)

        self.assertTrue(
            any(
                "expected one low_conflict and one high_conflict" in error
                for error in errors
            )
        )

    def test_mismatched_answers_are_detected(self):
        items = [
            {
                "pair_id": "pair_001",
                "condition": "low_conflict",
                "answer": "A",
            },
            {
                "pair_id": "pair_001",
                "condition": "high_conflict",
                "answer": "B",
            },
        ]

        _, errors = validate_pairs(items)

        self.assertTrue(
            any(
                "answers differ across conditions" in error
                for error in errors
            )
        )


if __name__ == "__main__":
    unittest.main()