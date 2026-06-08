from pathlib import Path
import re
import tempfile

from django.core.management import call_command
from django.core.management.base import CommandError
from django.template import Context, Template
from django.template.loader import render_to_string
from django.test import SimpleTestCase
from django.utils.safestring import SafeString

from bs_icon_templates.templatetags.bs_icons import bs_icon


def render(template_string, context=None):
    return Template(template_string).render(Context(context or {}))


def height_of(svg):
    """Return the value of the SVG's ``height`` attribute, or ``None``."""
    match = re.search(r'<svg[^>]*\bheight="([^"]*)"', svg)
    return match.group(1) if match else None


class DirectIncludeTests(SimpleTestCase):
    """Using {% include "bs_icon/<name>.svg" %} directly."""

    def test_renders_svg_markup(self):
        out = render('{% include "bs_icon/alarm.svg" %}')
        self.assertIn("<svg", out)
        self.assertIn("</svg>", out)
        self.assertIn("<path", out)
        self.assertIn('class="bi bi-alarm"', out)

    def test_default_height_is_16(self):
        out = render('{% include "bs_icon/alarm.svg" %}')
        self.assertEqual(height_of(out), "16")

    def test_custom_height_via_with(self):
        out = render('{% include "bs_icon/alarm.svg" with height=24 %}')
        self.assertEqual(height_of(out), "24")

    def test_custom_height_from_context_variable(self):
        out = render(
            '{% include "bs_icon/alarm.svg" with height=size %}',
            {"size": 48},
        )
        self.assertEqual(height_of(out), "48")

    def test_width_attribute_removed(self):
        out = render('{% include "bs_icon/alarm.svg" %}')
        self.assertNotIn("width=", out)

    def test_render_to_string_default_height(self):
        out = render_to_string("bs_icon/alarm.svg")
        self.assertEqual(height_of(out), "16")


class TemplateTagTests(SimpleTestCase):
    """Using {% bs_icon "<name>" %}."""

    def test_renders_svg_markup(self):
        out = render('{% load bs_icons %}{% bs_icon "alarm" %}')
        self.assertIn("<svg", out)
        self.assertIn("</svg>", out)
        self.assertIn("<path", out)
        self.assertIn('class="bi bi-alarm"', out)

    def test_default_height_is_16(self):
        out = render('{% load bs_icons %}{% bs_icon "alarm" %}')
        self.assertEqual(height_of(out), "16")

    def test_custom_height_keyword(self):
        out = render('{% load bs_icons %}{% bs_icon "alarm" height=24 %}')
        self.assertEqual(height_of(out), "24")

    def test_custom_height_from_context_variable(self):
        out = render(
            '{% load bs_icons %}{% bs_icon "alarm" height=size %}',
            {"size": 48},
        )
        self.assertEqual(height_of(out), "48")

    def test_width_attribute_removed(self):
        out = render('{% load bs_icons %}{% bs_icon "alarm" %}')
        self.assertNotIn("width=", out)

    def test_output_is_marked_safe(self):
        # Output must not be HTML-escaped when rendered in a template.
        result = bs_icon("alarm")
        self.assertIsInstance(result, SafeString)
        self.assertIn("<svg", render('{% load bs_icons %}{% bs_icon "alarm" %}'))

    def test_default_height_argument(self):
        self.assertEqual(height_of(bs_icon("alarm")), "16")

    def test_explicit_height_argument(self):
        self.assertEqual(height_of(bs_icon("alarm", height=32)), "32")

    def test_missing_icon_raises(self):
        from django.template import TemplateDoesNotExist

        with self.assertRaises(TemplateDoesNotExist):
            bs_icon("this-icon-does-not-exist")


class ParityTests(SimpleTestCase):
    """The template tag and include methods should produce identical output."""

    def test_include_and_tag_match_default(self):
        tag = render('{% load bs_icons %}{% bs_icon "alarm" %}')
        include = render('{% include "bs_icon/alarm.svg" %}')
        self.assertEqual(tag, include)

    def test_include_and_tag_match_custom_height(self):
        tag = render('{% load bs_icons %}{% bs_icon "alarm" height=24 %}')
        include = render('{% include "bs_icon/alarm.svg" with height=24 %}')
        self.assertEqual(tag, include)


class CopyBsIconsTests(SimpleTestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.output_dir = Path(self._tmp.name) / "templates" / "bs_icon"

    def _copy(self, *names, **opts):
        opts.setdefault("output_dir", str(self.output_dir))
        call_command("copy_bs_icons", *names, **opts)

    def test_copies_named_icon(self):
        self._copy("alarm")
        self.assertTrue((self.output_dir / "alarm.svg").is_file())

    def test_accepts_svg_suffix(self):
        self._copy("alarm.svg")
        self.assertTrue((self.output_dir / "alarm.svg").is_file())

    def test_copies_multiple_icons(self):
        self._copy("alarm", "gear")
        self.assertTrue((self.output_dir / "alarm.svg").is_file())
        self.assertTrue((self.output_dir / "gear.svg").is_file())

    def test_creates_missing_output_dir(self):
        self.assertFalse(self.output_dir.exists())
        self._copy("alarm")
        self.assertTrue(self.output_dir.is_dir())

    def test_copied_content_matches_source(self):
        self._copy("alarm")
        app_dir = Path(__import__("bs_icon_templates").__file__).resolve().parent
        src = app_dir / "templates" / "bs_icon" / "alarm.svg"
        dest = self.output_dir / "alarm.svg"
        self.assertEqual(dest.read_text(), src.read_text())

    def test_missing_icon_raises(self):
        with self.assertRaises(CommandError):
            self._copy("this-icon-does-not-exist")

    def test_custom_source_dir(self):
        source = Path(self._tmp.name) / "custom_source"
        source.mkdir()
        (source / "myicon.svg").write_text("<svg></svg>")
        self._copy("myicon", source_dir=str(source))
        self.assertEqual((self.output_dir / "myicon.svg").read_text(), "<svg></svg>")
