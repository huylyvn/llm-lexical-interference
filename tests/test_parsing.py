import os
import sys
import unittest

os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")

sys.path.insert(0, "src")

from run_eval import parse_answer, score_answer


class TestParsing(unittest.TestCase):

    def test_exact_letter_parses(self):
        for answer in ["A", "B", "C", "D"]:
            with self.subTest(answer=answer):
                self.assertEqual(parse_answer(answer), answer)

    def test_whitespace_is_ignored(self):
        self.assertEqual(parse_answer("  c  "), "C")

    def test_final_standalone_letter_parses(self):
        raw_output = """The context suggests one option is best.

B"""
        self.assertEqual(parse_answer(raw_output), "B")

    def test_explicit_answer_statement_parses(self):
        self.assertEqual(
            parse_answer("The answer is **D**."),
            "D",
        )

    def test_unsupported_verbose_answer_is_unscorable(self):
        self.assertIsNone(
            parse_answer("I think the best choice is A because of the context.")
        )

    def test_score_answer_correct(self):
        self.assertTrue(score_answer("B", "B"))

    def test_score_answer_incorrect(self):
        self.assertFalse(score_answer("A", "B"))

    def test_unparsed_answer_remains_unscorable(self):
        self.assertIsNone(score_answer(None, "A"))


if __name__ == "__main__":
    unittest.main()