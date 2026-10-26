from datetime import date, datetime

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from cases.models import Case
from evidence.models import Evidence
from .forms import SuspectForm
from .models import Alibi, Suspect


def aware(*args):
    return timezone.make_aware(datetime(*args))


class AlibiModelTests(TestCase):
    def setUp(self):
        self.suspect = Suspect.objects.create(first_name='Георги', last_name='Димитров')
        Alibi.objects.create(
            suspect=self.suspect,
            location='Ресторант „Мрежата“',
            starts_at=aware(2024, 1, 15, 20),
            ends_at=aware(2024, 1, 15, 23),
        )

    def test_end_must_be_after_start(self):
        alibi = Alibi(
            suspect=self.suspect,
            location='Вкъщи',
            starts_at=aware(2024, 2, 1, 12),
            ends_at=aware(2024, 2, 1, 11),
        )

        with self.assertRaises(ValidationError) as error:
            alibi.full_clean()

        self.assertIn('ends_at', error.exception.message_dict)

    def test_overlapping_alibi_in_another_place_is_rejected(self):
        alibi = Alibi(
            suspect=self.suspect,
            location='Кино Арена',
            starts_at=aware(2024, 1, 15, 22),
            ends_at=aware(2024, 1, 16, 1),
        )

        with self.assertRaisesMessage(ValidationError, 'противоречи'):
            alibi.full_clean()

    def test_overlapping_alibi_in_same_place_is_allowed(self):
        alibi = Alibi(
            suspect=self.suspect,
            location='ресторант „мрежата“',
            starts_at=aware(2024, 1, 15, 22),
            ends_at=aware(2024, 1, 16, 1),
        )

        alibi.full_clean()


class SuspectTests(TestCase):
    def setUp(self):
        self.case = Case.objects.create(
            title='Кражбата', description='-', crime_date=date(2024, 1, 1), location='Варна',
        )
        self.suspect = Suspect.objects.create(first_name='Иван', last_name='Петров', alias='Шефа')
        self.suspect.cases.add(self.case)

    def test_full_name_includes_alias(self):
        self.assertEqual(self.suspect.full_name, 'Иван Петров „Шефа“')

    def test_suspicion_index_counts_evidence(self):
        Evidence.objects.create(case=self.case, title='Отпечатък', collected_on=date(2024, 1, 2), implicates=self.suspect)

        suspect = Suspect.objects.with_suspicion().get(pk=self.suspect.pk)

        self.assertEqual(suspect.suspicion_index, 1)

    def test_cannot_unlink_case_with_implicating_evidence(self):
        Evidence.objects.create(case=self.case, title='Отпечатък', collected_on=date(2024, 1, 2), implicates=self.suspect)
        form = SuspectForm(instance=self.suspect, data={'first_name': 'Иван', 'last_name': 'Петров', 'cases': []})

        self.assertFalse(form.is_valid())
        self.assertIn('cases', form.errors)

    def test_alibi_create_redirects_to_suspect(self):
        response = self.client.post(reverse('suspects:alibi-create', args=[self.suspect.pk]), {
            'location': 'Вкъщи',
            'starts_at': '2024-03-01T10:00',
            'ends_at': '2024-03-01T12:00',
        })

        self.assertRedirects(response, self.suspect.get_absolute_url())
        self.assertEqual(self.suspect.alibis.count(), 1)
