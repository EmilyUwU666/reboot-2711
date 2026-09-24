import unittest
from inspect_network_contracts import classify_thread_report, EXPECTED

class ThreadReportTests(unittest.TestCase):
    def report(self, value, status=5, state=3):
        return {"ExecutableSha256": EXPECTED, "Callback": {"State": state,
            "ThreadContext": {"Status": status, "RawValue": value}}}
    def test_observed_game_thread_value(self):
        result=classify_thread_report(self.report(2))
        self.assertTrue(result["MatchesObservedGameThreadPredicate"])
        self.assertFalse(result["NetworkingCallsApproved"])
    def test_fallback_is_unknown(self):
        self.assertIsNone(classify_thread_report(self.report(1))["MatchesObservedGameThreadPredicate"])
    def test_other_values_fail_this_predicate(self):
        for value in (0, 16, 0xffffffff):
            self.assertFalse(classify_thread_report(self.report(value))["MatchesObservedGameThreadPredicate"])
    def test_incomplete_or_rejected_observations(self):
        for report in (None, {}, self.report(2, status=1), self.report(2, state=2),
                       self.report(True), self.report(-1), self.report(2**32)):
            self.assertFalse(classify_thread_report(report)["Observed"])
    def test_wrong_image(self):
        report=self.report(2);report["ExecutableSha256"]="different"
        self.assertFalse(classify_thread_report(report)["Observed"])

if __name__ == "__main__": unittest.main()
