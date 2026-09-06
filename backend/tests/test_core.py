import unittest

from ai.model_registry import ROLES
from premium import premium_view, plan_payload


class RoboLabCoreTests(unittest.TestCase):
    def test_has_exactly_48_specialist_slots(self):
        self.assertEqual(len(ROLES), 48)
        self.assertEqual(len({role.id for role in ROLES}), 48)

    def test_free_plan_hides_specialist_reports(self):
        result = {"summary": "x", "agent_reports": [{"role": "test"}]}
        viewed = premium_view(result, "free")
        self.assertNotIn("agent_reports", viewed)
        self.assertFalse(viewed["premium"]["enabled"])

    def test_pro_plan_keeps_specialist_reports(self):
        result = {"summary": "x", "agent_reports": [{"role": "test"}]}
        viewed = premium_view(result, "pro")
        self.assertIn("agent_reports", viewed)
        self.assertTrue(viewed["premium"]["enabled"])

    def test_beta_plan_is_server_configurable(self):
        self.assertIn(plan_payload()["id"], {"free", "pro", "studio"})


if __name__ == "__main__":
    unittest.main()
