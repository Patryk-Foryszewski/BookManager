from django.conf import settings
from django.template import Context, Template
from django.test import SimpleTestCase, TestCase

from bookmanager.books.filters import InternalBooksFilter
from bookmanager.books.templatetags.books_tags import (
    count_book_index,
    google_search_form,
    internal_search_form,
)
from bookmanager.books.utils import create_paginator, get_paginator_page


class CountBookIndexTemplateTagTest(SimpleTestCase):
    def test_first_book_index(self):
        first = count_book_index(page=1, index=1)
        self.assertEqual(first, 1)

    def test_second_page_first_book_index(self):
        outcome = count_book_index(page=2, index=1)
        self.assertEqual(outcome, settings.PAGINATE_BY + 1)


class InternalSearchFormTemplateTagTest(TestCase):
    def test_context(self):
        filters = {"search": "gropius", "title": "architecture"}
        context = internal_search_form(InternalBooksFilter(filters))
        keys = context.keys()
        [self.assertTrue(key in keys) for key in ["action", "filter"]]
        self.assertDictEqual(filters, context["filter"].data)


class GoogleSearchFormTemplateTagTest(SimpleTestCase):
    def test_context(self):
        query_dict = {"search": "a", "intitle": "b", "inauthor": "c"}
        context = google_search_form(query_dict)
        keys = context.keys()

        [self.assertTrue(key in keys) for key in ["action", *query_dict.keys()]]

    def test_wrong_query_type(self):
        context = google_search_form("-")
        self.assertEqual(len(context.keys()), 1)


class CoverFrameTemplateTagTest(SimpleTestCase):
    def test_rendered(self):
        cover_uri = "nice_pic.jpg"
        context = Context({"cover_uri": cover_uri})
        template_to_render = Template(
            "{% load books_tags %}" "{% cover_frame cover_uri %}"
        )
        rendered_template = template_to_render.render(context)
        pattern_1 = f'<a href="{cover_uri}">'
        # self.assertInHTML(pattern_1, rendered_template) - doesn't work
        self.assertTrue(pattern_1 in rendered_template)

        pattern_2 = f'<img src="{cover_uri}"'
        # self.assertInHTML(pattern_2, rendered_template) - doesn't work
        self.assertTrue(pattern_2 in rendered_template)


class PaginationTemplateTagTest(SimpleTestCase):
    total = 200
    items = ["#" for _ in range(settings.PAGINATE_BY)]
    paginator = create_paginator(items, total, 1)
    page_obj = get_paginator_page(paginator, 1)

    def test_pagination_wiouth_previous_page(self):

        context = Context({"search": "search=Px48", "page_obj": self.page_obj})

        template_to_render = Template(
            "{% load books_tags %}" "{% pagination page_obj search%}"
        )
        rendered_template = template_to_render.render(context)
        self.assertTrue("previous" not in rendered_template)

    def test_pagination_with_previous_page(self):
        paginator = create_paginator(self.items, self.total, 2)
        page_obj = get_paginator_page(paginator, 2)

        context = Context({"search": "search=Px48", "page_obj": page_obj})

        template_to_render = Template(
            "{% load books_tags %}" "{% pagination page_obj search%}"
        )
        rendered_template = template_to_render.render(context)
        self.assertTrue("previous" in rendered_template)

    def test_pagination_witouth_next_page(self):
        paginator = create_paginator(self.items, 40, 1)
        page_obj = get_paginator_page(paginator, 1)

        context = Context({"search": "search=Px48", "page_obj": page_obj})

        template_to_render = Template(
            "{% load books_tags %}" "{% pagination page_obj search%}"
        )
        rendered_template = template_to_render.render(context)
        self.assertTrue("next" not in rendered_template)

    def test_pagination_with_next_page(self):

        context = Context({"search": "search=Px48", "page_obj": self.page_obj})

        template_to_render = Template(
            "{% load books_tags %}" "{% pagination page_obj search%}"
        )
        rendered_template = template_to_render.render(context)
        self.assertTrue("next" in rendered_template)
