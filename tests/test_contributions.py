"""Calendar boundary and data-quality cases that would misstate public statistics."""
import datetime
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from fetch_contributions import build_data, compute_current_streak


def calendar(start, counts):
    first = datetime.date.fromisoformat(start)
    return [
        {"date": (first + datetime.timedelta(days=i)).isoformat(), "count": count, "level": 0}
        for i, count in enumerate(counts)
    ]


class ContributionTests(unittest.TestCase):
    def test_unfinished_today_keeps_yesterdays_streak(self):
        days = calendar("2026-11-20", [3, 1, 0])
        self.assertEqual(
            compute_current_streak(days, datetime.date(2026, 11, 22)),
            (2, "2026-11-20", "2026-11-21"),
        )

    def test_zero_yesterday_breaks_streak_even_if_today_is_missing(self):
        days = calendar("2026-11-20", [3, 0])
        self.assertEqual(
            compute_current_streak(days, datetime.date(2026, 11, 22)),
            (0, None, None),
        )

    def test_today_and_leap_day_count_as_consecutive_days(self):
        days = calendar("2024-02-28", [1, 2, 3])
        data = build_data(days, today=datetime.date(2024, 3, 1))
        self.assertEqual(data["current_streak"]["length"], 3)
        self.assertEqual(data["longest_streak"]["length"], 3)
        self.assertEqual(data["monthly"], [
            {"month": "2024-02", "total": 3}, {"month": "2024-03", "total": 3},
        ])

    def test_zero_activity_is_valid(self):
        data = build_data(calendar("2026-11-20", [0, 0, 0]), today=datetime.date(2026, 11, 22))
        self.assertEqual(data["total_contributions"], 0)
        self.assertEqual(data["avg_per_active_day"], 0)
        self.assertEqual(data["longest_streak"]["length"], 0)

    def test_missing_duplicate_and_negative_counts_are_rejected(self):
        days = calendar("2026-11-20", [1, 2, 3])
        cases = [[], days[::2], [days[0], days[0]], calendar("2026-11-20", [-1])]
        for invalid in cases:
            with self.subTest(days=invalid), self.assertRaises(ValueError):
                build_data(invalid)

    def test_monthly_totals_include_both_boundary_months(self):
        data = build_data(calendar("2025-11-23", [1] * 365), today=datetime.date(2026, 11, 22))
        self.assertEqual(len(data["monthly"]), 13)
        self.assertEqual(sum(month["total"] for month in data["monthly"]), 365)
        self.assertEqual(data["total_contributions"], 365)


if __name__ == "__main__":
    unittest.main()
