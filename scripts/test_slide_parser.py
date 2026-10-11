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

    def test_slide_class_attribute_variants(self):
        body = '<div class="slide-content"><h1>Title</h1></div></section>'
        for attr in ('class="slide "', 'class=" slide"', "class='slide'", 'class = "slide"'):
            self.assertEqual(checks.check_structure(f'<section {attr}>{body}' * 3), (3, []), attr)
        self.assertEqual(checks.check_structure(f'<section data-class="slide">{body}' * 3)[0], 0)
        # Cohort and deliverable checks reuse SLIDE_OPEN with single-quoted class.
        housekeeping = f"<section class='slide' aria-label=\"Housekeeping\"><div class=\"slide-content\"><h1>H</h1>November 26, 2026</div></section>"
        self.assertEqual(checks.check_cohort_generic(housekeeping), [])
        deliverable = "<section class='slide '><h1 class=\"slide-title\">Thing</h1><span class=\"symbol-badge\"></span></section>"
        self.assertEqual(checks.check_deliverable_links(deliverable)[0], ["Deliverable slide 'Thing' missing: Article, AI Prompt"])


class StyleTests(unittest.TestCase):
    def test_dashes_literal_and_entities_flagged(self):
        for text in ('a — b', 'a – b', 'a &mdash; b', 'a &ndash; b',
                     'a &#8212; b', 'a &#8211; b', 'a &#x2014; b', 'a &#x2013; b'):
            issues = checks.check_style(f'<p>{text}</p>')
            self.assertTrue(any('em or en dash' in s for s in issues), text)

    def test_hyphen_not_flagged(self):
        self.assertEqual(checks.check_style('<p>a - b, 10-15 minutes</p>'), [])


class TimeChainTests(unittest.TestCase):
    def span(self, t):
        return f'<span class="time-indicator">({t})</span>'

    def test_backwards_clock_flagged(self):
        n, issues = checks.check_time_chain(self.span('10') + self.span('5'))
        self.assertEqual(n, 2)
        self.assertIn('Indicator 2: time moves backwards from 10 to 5', issues)

    def test_forward_clock_passes(self):
        self.assertEqual(checks.check_time_chain(self.span('5') + self.span('10')), (2, []))


class LinkAndImageTests(unittest.TestCase):
    base = Path(__file__).parent

    def test_fragment_links(self):
        ok_html = '<div id="target"></div><span id=\'other\'></span><a href="#target">t</a><a href=\'#other\'>o</a><a href="#">top</a>'
        oks, issues = checks.check_links(ok_html, self.base)
        self.assertEqual(issues, [])
        self.assertEqual(len(oks), 3)
        oks, issues = checks.check_links('<a href="#missing">m</a>', self.base)
        self.assertEqual(len(issues), 1)
        self.assertIn('#missing', issues[0])

    def test_skipped_schemes(self):
        html = '<a href="mailto:x@example.com">m</a><a href="tel:123">t</a><a href="javascript:void(0)">j</a>'
        self.assertEqual(checks.check_links(html, self.base), ([], []))

    def test_single_quoted_src_and_href(self):
        name = Path(__file__).name
        oks, issues = checks.check_images(f"<img alt='x' src='{name}'><img src='missing.png'>", self.base)
        self.assertEqual(len(oks), 1)
        self.assertEqual(len(issues), 1)
        self.assertIn('missing.png', issues[0])
        oks, issues = checks.check_links(f"<a class='x' href='{name}'>f</a><a href='nope.html'>n</a>", self.base)
        self.assertEqual(len(oks), 1)
        self.assertEqual(len(issues), 1)
        self.assertIn('nope.html', issues[0])

    def test_link_tag_ignored(self):
        self.assertEqual(checks.check_links('<link href="missing.css" rel="stylesheet">', self.base), ([], []))

if __name__ == '__main__':
    unittest.main()
