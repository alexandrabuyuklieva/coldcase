from datetime import timedelta

from django.template import Context, Template
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from cases.forms import CaseFilterForm
from evidence.forms import EvidenceFilterForm
from common.templatetags.coldcase_tags import days_since, suspicion_level


class TemplateTagTests(TestCase):
    def test_suspicion_level(self):
        self.assertEqual(suspicion_level(0), 'нисък')
        self.assertEqual(suspicion_level(2), 'среден')
        self.assertEqual(suspicion_level(5), 'висок')
        self.assertEqual(suspicion_level('abc'), 'нисък')

    def test_days_since(self):
        today = timezone.localdate()

        self.assertEqual(days_since(today), 'днес')
        self.assertEqual(days_since(today - timedelta(days=1)), '1 ден')
        self.assertEqual(days_since(today - timedelta(days=12)), '12 дни')

    def test_confidence_meter_is_clamped(self):
        html = Template('{% load coldcase_tags %}{% confidence_meter value %}').render(Context({'value': 180}))

        self.assertIn('width: 100%', html)


class HomeViewTests(TestCase):
    def test_home_page_works_with_empty_database(self):
        response = self.client.get(reverse('common:home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Няма открити досиета')


class SortableFilterFormTests(TestCase):
    def test_default_ordering_is_used_for_unknown_sort(self):
        form = CaseFilterForm({'sort': 'unknown'})

        self.assertEqual(form.ordering(), CaseFilterForm.SORT_ORDERING['newest'])

    def test_sort_field_is_rendered_last(self):
        self.assertEqual(list(EvidenceFilterForm().fields)[-1], 'sort')
