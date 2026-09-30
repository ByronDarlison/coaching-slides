"""Regression checks for legacy and shared-shell section markup."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('slide_test', Path(__file__).with_name('slide-test.py'))
checks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checks)

class SlideMarkupTests(unittest.TestCase):
    def slide(self, label='Teaching', content='<h1>Title</h1>', modern=True):
        attrs = f'aria-label="{label}" class="slide comp-story"' if modern else f'class="slide" aria-label="{label}"'
        return f'<section {attrs}><div class="slide-content">{content}</div></section>'

    def test_structure_in_both_formats(self):
        for modern in (True, False):
            self.assertEqual(checks.check_structure(self.slide(modern=modern) * 3), (3, []))
        self.assertTrue(checks.check_structure(self.slide(content='No heading') * 3)[1])
        self.assertEqual(checks.check_structure('<section class="slide-content"></section>')[0], 0)

    def test_dates_exempt_only_in_named_sections(self):
        for modern in (True, False):
            for label in ('Housekeeping', 'Sample 3HAG'):
                self.assertEqual(checks.check_cohort_generic(self.slide(label, 'November 26, 2026', modern)), [])
            self.assertTrue(checks.check_cohort_generic(self.slide('Teaching', 'November 26, 2026', modern)))

    def test_homework_still_required(self):
        for modern in (True, False):
            self.assertTrue(checks.check_homework_deadline(self.slide('Homework', 'Missing deadline', modern)))
            self.assertEqual(checks.check_homework_deadline(self.slide('Homework', checks.HOMEWORK_DEADLINE_PHRASE, modern)), [])

if __name__ == '__main__':
    unittest.main()
