from __future__ import annotations

import unittest

from learning_compiler.validator.rules import RULES


class ValidatorRuleRegistryTests(unittest.TestCase):
    def test_rule_ids_are_unique_and_stable_shape(self) -> None:
        rule_ids = [rule.rule_id for rule in RULES]
        self.assertEqual(len(rule_ids), len(set(rule_ids)))
        self.assertTrue(rule_ids[0].startswith("schema."))
        self.assertTrue(rule_ids[-1].startswith("evidence."))


if __name__ == "__main__":
    unittest.main()

