import unittest
from decimal import Decimal
from unittest.mock import patch

import data


class GeneratorTests(unittest.TestCase):
    @patch("data.insert_data", return_value=6)
    def test_prices_single_batch_and_ranges(self, insert):
        data.generate_stock_prices(None, ["AAA", "BBB"], days=3)
        insert.assert_called_once()
        _, query, rows = insert.call_args.args
        self.assertIn("dailyMin", query)
        self.assertEqual(len(rows), 6)
        self.assertEqual(len({(r[0], r[1]) for r in rows}), 6)
        for _, day, opening, closing, high, low in rows:
            self.assertLess(day.weekday(), 5)
            self.assertGreater(low, Decimal(0))
            self.assertTrue(low <= opening <= high)
            self.assertTrue(low <= closing <= high)

    @patch("data.fetch_one", return_value=(0,))
    @patch("data.insert_data", return_value=20)
    def test_revenue_single_batch(self, insert, fetch):
        data.generate_revenue_reports(None, [1, 2])
        insert.assert_called_once()
        rows = insert.call_args.args[2]
        self.assertEqual(len(rows), 20)
        self.assertEqual(len({r[0] for r in rows}), 20)
        self.assertEqual(len({(r[1], r[2]) for r in rows}), 20)

    @patch("data.fake.company", return_value="Existing")
    @patch("data.fetch_one", return_value=(1,))
    @patch("data.fetch_all", side_effect=[[("Existing",)], [(1,), (2,), (3,)]])
    @patch("data.insert_data", return_value=2)
    def test_duplicate_company_names(self, insert, fetch_all, fetch_one, company):
        data.generate_companies(None, count=2)
        rows = insert.call_args.args[2]
        self.assertEqual([r[0] for r in rows], [2, 3])
        self.assertEqual([r[1] for r in rows], ["Existing (1)", "Existing (2)"])


if __name__ == "__main__":
    unittest.main()
