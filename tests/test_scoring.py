import unittest

from sre import config, cli, scoring, signals


def base_account(**kw):
    a = {
        "id": "X-001", "client": "lumora", "name": "Test", "arr": 400000,
        "seats_licensed": 100, "seats_active": 75,
        "modules_licensed": ["A", "B", "C", "D", "E"], "modules_used": ["A", "B", "C", "D"],
        "addons_licensed": [], "tickets_monthly": [30] * 6, "tickets_90d": 90,
        "escalations_90d": 6, "sev1_90d": 1, "reopen_rate": 0.08, "sentiment": 0.3, "csat": 4.5,
        "churn_mentions_90d": 0, "usage_trend": 0.05, "days_since_exec_touch": 20, "champion_left": False,
        "howto_by_use_case": {"A": [10, 10, 10, 10, 10, 10]},
    }
    a.update(kw)
    return a


class ScoringTest(unittest.TestCase):
    def setUp(self):
        self.cfg = config.load()

    def test_healthy_account_is_green(self):
        r = scoring.score_account(base_account(), self.cfg)
        self.assertEqual(r["band"], "green")
        self.assertLess(r["churn_probability"], 0.1)

    def test_escalation_storm_goes_red_and_names_driver(self):
        acc = base_account(escalations_90d=25, sev1_90d=8, reopen_rate=0.45, sentiment=-0.5, csat=2.4, churn_mentions_90d=3)
        r = scoring.score_account(acc, self.cfg)
        self.assertEqual(r["band"], "red")
        self.assertEqual(r["primary_driver"], "escalation")

    def test_drifting_account_flags_disengagement(self):
        acc = base_account(usage_trend=-0.4, days_since_exec_touch=150, champion_left=True, seats_active=45, modules_used=["A", "B"])
        r = scoring.score_account(acc, self.cfg)
        self.assertNotEqual(r["band"], "green")
        self.assertEqual(r["primary_driver"], "disengagement")

    def test_query_surge_on_unowned_addon_creates_pipeline(self):
        acc = base_account(howto_by_use_case={"Bots": [1, 1, 2, 2, 2, 9]})
        r = scoring.score_account(acc, self.cfg)
        self.assertEqual(r["expansion"]["surges"][0]["use_case"], "Bots")
        self.assertGreater(r["expansion"]["pipeline_value"], 0)

    def test_surge_on_owned_addon_is_ignored(self):
        acc = base_account(addons_licensed=["Bots"], howto_by_use_case={"Bots": [1, 1, 2, 2, 2, 9]})
        self.assertEqual(scoring.score_account(acc, self.cfg)["expansion"]["surges"], [])

    def test_red_account_is_not_pitched(self):
        acc = base_account(escalations_90d=30, sev1_90d=9, reopen_rate=0.5, sentiment=-0.6, csat=2.0,
                           churn_mentions_90d=4, seats_active=95, howto_by_use_case={"Bots": [1, 1, 1, 1, 1, 10]})
        r = scoring.score_account(acc, self.cfg)
        self.assertEqual(r["band"], "red")
        self.assertTrue(r["expansion"]["blocked_by_risk"])
        self.assertEqual(r["expansion"]["pipeline_value"], 0)

    def test_whatif_escalation_cut_lowers_risk(self):
        acc = base_account(escalations_90d=25, sev1_90d=8, reopen_rate=0.45)
        before = scoring.score_account(acc, self.cfg)["churn_probability"]
        after = scoring.score_account(acc, self.cfg, {"escalation_reduction": 0.5})["churn_probability"]
        self.assertLess(after, before)

    def test_sentiment_lexicon(self):
        self.assertGreater(signals.sentiment("Thanks, resolved quickly, great help")[0], 0)
        s, churn = signals.sentiment("We are reviewing alternatives before the renewal")
        self.assertLess(s, 0)
        self.assertTrue(churn)


class PipelineTest(unittest.TestCase):
    def test_pipeline_runs_and_finds_planted_risk(self):
        cfg = config.load()
        tickets, scored, actions, summary = cli.run(cfg)
        self.assertGreater(len(tickets), 30000)
        self.assertEqual(summary["total"]["accounts"], 100)
        quality = cli.evaluate(scored)
        self.assertGreaterEqual(quality["precision"], 0.8)
        self.assertGreaterEqual(quality["recall"], 0.8)
        self.assertTrue(all(a["owner"] and a["start_within_days"] for a in actions))


if __name__ == "__main__":
    unittest.main()
