from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from evidence.models import Evidence
from .forms import CaseForm
from .models import Case


def create_case(**kwargs):
    data = {
        'title': 'Убийството в Боровец',
        'description': 'Тялото е открито рано сутринта.',
        'crime_date': date(2024, 1, 15),
        'location': 'Самоков',
    }
    data.update(kwargs)
    return Case.objects.create(**data)


class CaseModelTests(TestCase):
    def test_case_number_is_generated_sequentially(self):
        year = timezone.localdate().year
        first = create_case()
        second = create_case(title='Изчезналата картина')

        self.assertEqual(first.case_number, f'CC-{year}-0001')
        self.assertEqual(second.case_number, f'CC-{year}-0002')

    def test_crime_date_cannot_be_in_the_future(self):
        case = Case(
            title='Бъдеще',
            description='-',
            crime_date=timezone.localdate() + timedelta(days=1),
            location='София',
        )

        with self.assertRaises(ValidationError) as error:
            case.full_clean(exclude=['case_number'])

        self.assertIn('crime_date', error.exception.message_dict)

    def test_crime_date_cannot_move_after_existing_evidence(self):
        case = create_case()
        Evidence.objects.create(case=case, title='Нож', collected_on=date(2024, 1, 16))
        case.crime_date = date(2024, 2, 1)

        with self.assertRaises(ValidationError):
            case.full_clean()


class CaseFormTests(TestCase):
    def test_case_number_is_read_only_when_editing(self):
        case = create_case()
        form = CaseForm(instance=case)

        self.assertTrue(form.fields['case_number'].disabled)
        self.assertEqual(form.fields['case_number'].initial, case.case_number)

    def test_case_number_is_hidden_when_creating(self):
        self.assertNotIn('case_number', CaseForm().fields)

    def test_custom_required_message(self):
        form = CaseForm(data={})

        self.assertIn('Всяко досие има нужда от заглавие.', form.errors['title'])


class CaseViewTests(TestCase):
    def test_create_redirects_to_detail(self):
        response = self.client.post(reverse('cases:create'), {
            'title': 'Отровата',
            'description': 'Отравяне на прием.',
            'crime_date': '2023-05-10',
            'location': 'Пловдив',
            'status': Case.Status.OPEN,
        })

        case = Case.objects.get()
        self.assertRedirects(response, case.get_absolute_url())

    def test_list_filters_by_status(self):
        create_case(title='Открит случай')
        create_case(title='Разкрит случай', status=Case.Status.SOLVED)

        response = self.client.get(reverse('cases:list'), {'status': Case.Status.SOLVED})

        self.assertContains(response, 'Разкрит случай')
        self.assertNotContains(response, 'Открит случай')

    def test_delete_requires_confirmation(self):
        case = create_case()

        response = self.client.get(reverse('cases:delete', args=[case.pk]))

        self.assertContains(response, 'Потвърдете изтриването')
        self.assertTrue(Case.objects.exists())

    def test_unknown_page_uses_custom_404(self):
        response = self.client.get('/no-such-page/')

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')
