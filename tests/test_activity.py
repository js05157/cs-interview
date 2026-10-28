from datetime import date
import unittest
from scripts.activity import parse_calendar,snapshot

class ActivityTests(unittest.TestCase):
    def test_dates_and_counts_are_read_from_source_not_synthesized(self):
        html='<td id="a" data-date="2026-01-01" data-level="0"></td><tool-tip for="a">No contributions on January 1st.</tool-tip><td id="b" data-date="2026-01-02" data-level="3"></td><tool-tip for="b">1,234 contributions on January 2nd.</tool-tip>'
        days=parse_calendar(html,'2026-01-01','2026-01-02')
        self.assertEqual([d['count'] for d in days],[0,1234])
        result=snapshot('js05157',2026,html=html,today=date(2026,1,2))
        self.assertEqual(result['total'],1234)
    def test_missing_days_or_changed_tooltips_fail_closed(self):
        with self.assertRaises(ValueError):parse_calendar('','2026-01-01','2026-01-02')
        with self.assertRaises(ValueError):parse_calendar('<td id="x" data-date="2026-01-01" data-level="2"></td>','2026-01-01','2026-01-01')
