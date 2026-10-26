from django import forms

from common.forms import DisabledFieldsMixin, SortableFilterForm, StyledFormMixin
from suspects.models import Suspect
from .models import Evidence


class EvidenceForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Evidence
        exclude = ('created_at', 'updated_at')
        widgets = {
            'collected_on': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'confidence': forms.NumberInput(attrs={'min': 0, 'max': 100}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'case': 'Досие',
            'title': 'Наименование',
            'evidence_type': 'Вид улика',
            'collected_on': 'Дата на откриване',
            'found_at': 'Място на откриване',
            'confidence': 'Достоверност (%)',
            'implicates': 'Уличава',
            'description': 'Описание',
        }
        help_texts = {
            'collected_on': 'Не може да е преди престъплението или в бъдещето.',
            'confidence': 'От 0 до 100. Колко сигурни сте в уликата.',
            'implicates': 'Само заподозрени, свързани с досието.',
        }
        error_messages = {
            'case': {
                'required': 'Изберете към кое досие е уликата.',
            },
            'title': {
                'required': 'Дайте име на уликата.',
                'max_length': 'Наименованието е твърде дълго (максимум %(limit_value)d символа).',
            },
            'collected_on': {
                'required': 'Посочете кога е открита уликата.',
                'invalid': 'Въведете валидна дата.',
            },
            'confidence': {
                'invalid': 'Въведете цяло число.',
            },
        }

    placeholders = {
        'title': 'Окървавен нож',
        'found_at': 'Под леглото в стая 214',
        'description': 'Кухненски нож с дървена дръжка...',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['implicates'].empty_label = 'Никого'
        if self.instance.case_id:
            self.fields['implicates'].queryset = Suspect.objects.filter(cases=self.instance.case_id)


class EvidenceEditForm(DisabledFieldsMixin, EvidenceForm):
    disabled_fields = ('case',)


class EvidenceFilterForm(SortableFilterForm):
    SORT_CHOICES = (
        ('newest', 'Най-скоро открити'),
        ('oldest', 'Най-отдавна открити'),
        ('confidence', 'Най-достоверни'),
    )
    SORT_ORDERING = {
        'newest': ('-collected_on', '-created_at'),
        'oldest': ('collected_on', 'created_at'),
        'confidence': ('-confidence', '-collected_on'),
    }
    DEFAULT_SORT = 'newest'

    q = forms.CharField(
        required=False,
        label='Търсене',
        widget=forms.TextInput(attrs={'placeholder': 'Наименование, място...'}),
    )
    evidence_type = forms.ChoiceField(
        required=False,
        label='Вид',
        choices=(('', 'Всички'), *Evidence.EvidenceType.choices),
    )
