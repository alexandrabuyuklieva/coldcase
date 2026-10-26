from django import forms

from common.forms import SortableFilterForm, StyledFormMixin
from .models import Case


class CaseForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Case
        exclude = ('created_at', 'updated_at')
        widgets = {
            'crime_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'description': forms.Textarea(attrs={'rows': 5}),
        }
        labels = {
            'title': 'Заглавие на случая',
            'crime_date': 'Дата на престъплението',
            'location': 'Място на престъплението',
            'victim': 'Жертва',
            'description': 'Обстоятелства',
            'status': 'Статус на разследването',
        }
        help_texts = {
            'title': 'Кратко и запомнящо се име, например „Убийството в Боровец“.',
            'crime_date': 'Не може да е в бъдещето.',
            'victim': 'Оставете празно, ако няма пострадал.',
            'status': 'Замразените случаи може да бъдат отворени отново по всяко време.',
        }
        error_messages = {
            'title': {
                'required': 'Всяко досие има нужда от заглавие.',
                'max_length': 'Заглавието е твърде дълго (максимум %(limit_value)d символа).',
            },
            'description': {
                'required': 'Опишете какво се е случило.',
            },
            'crime_date': {
                'required': 'Посочете кога е извършено престъплението.',
                'invalid': 'Въведете валидна дата.',
            },
            'location': {
                'required': 'Посочете къде е извършено престъплението.',
            },
        }

    placeholders = {
        'title': 'Убийството в Боровец',
        'location': 'гр. Самоков, хотел „Ела“',
        'victim': 'Иван Петров',
        'description': 'Тялото е открито в 06:30 от камериерката...',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self._add_read_only_case_number()

    def _add_read_only_case_number(self):
        self.fields['case_number'] = forms.CharField(
            label='Номер на досието',
            initial=self.instance.case_number,
            disabled=True,
            required=False,
            help_text='Генерира се автоматично и не може да се променя.',
            widget=forms.TextInput(attrs={'class': 'form-input'}),
        )
        self.order_fields(['case_number', *self.Meta.labels])


class CaseFilterForm(SortableFilterForm):
    SORT_CHOICES = (
        ('newest', 'Най-нови престъпления'),
        ('oldest', 'Най-стари престъпления'),
        ('title', 'Заглавие (А-Я)'),
        ('evidence', 'Най-много улики'),
    )
    SORT_ORDERING = {
        'newest': ('-crime_date', '-created_at'),
        'oldest': ('crime_date', 'created_at'),
        'title': ('title',),
        'evidence': ('-evidence_count', '-crime_date'),
    }
    DEFAULT_SORT = 'newest'

    q = forms.CharField(
        required=False,
        label='Търсене',
        widget=forms.TextInput(attrs={'placeholder': 'Заглавие, номер, място...'}),
    )
    status = forms.ChoiceField(
        required=False,
        label='Статус',
        choices=(('', 'Всички'), *Case.Status.choices),
    )
