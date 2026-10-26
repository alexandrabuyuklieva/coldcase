from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from cases.models import Case
from suspects.models import Suspect
from .forms import EvidenceEditForm
from .models import Evidence


class EvidenceTests(TestCase):
    def setUp(self):
        self.case = Case.objects.create(
            title='Изчезналата картина', description='-', crime_date=date(2024, 3, 10), location='София',
        )

    def test_cannot_be_collected_before_crime(self):
        evidence = Evidence(case=self.case, title='Ключ', collected_on=date(2024, 3, 1))

        with self.assertRaises(ValidationError) as error:
            evidence.full_clean()

        self.assertIn('collected_on', error.exception.message_dict)

    def test_implicated_suspect_must_belong_to_case(self):
        stranger = Suspect.objects.create(first_name='Мария', last_name='Колева')
        evidence = Evidence(case=self.case, title='Ключ', collected_on=date(2024, 3, 11), implicates=stranger)

        with self.assertRaises(ValidationError) as error:
            evidence.full_clean()

        self.assertIn('implicates', error.exception.message_dict)

    def test_confidence_is_limited_to_100(self):
        evidence = Evidence(case=self.case, title='Ключ', collected_on=date(2024, 3, 11), confidence=150)

        with self.assertRaises(ValidationError):
            evidence.full_clean()

    def test_case_is_disabled_when_editing(self):
        evidence = Evidence.objects.create(case=self.case, title='Ключ', collected_on=date(2024, 3, 11))

        self.assertTrue(EvidenceEditForm(instance=evidence).fields['case'].disabled)

    def test_delete_redirects_to_case(self):
        evidence = Evidence.objects.create(case=self.case, title='Ключ', collected_on=date(2024, 3, 11))

        response = self.client.post(reverse('evidence:delete', args=[evidence.pk]))

        self.assertRedirects(response, self.case.get_absolute_url())
        self.assertFalse(Evidence.objects.exists())
