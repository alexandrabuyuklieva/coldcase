from django import forms
from django.core.exceptions import ValidationError

from cases.models import Case
from common.forms import StyledFormMixin
from .models import Alibi, Suspect


class SuspectForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Suspect
        exclude = ('created_at', 'updated_at')
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'description': forms.Textarea(attrs={'rows': 4}),
            'cases': forms.CheckboxSelectMultiple(),
        }
        labels = {
            'first_name': 'Име',
            'last_name': 'Фамилия',
            'alias': 'Прякор',
            'date_of_birth': 'Дата на раждане',
            'photo_url': 'Снимка (линк)',
            'description': 'Описание',
            'cases': 'Замесен в досиета',
        }
        help_texts = {
            'alias': 'С какво име го знаят на улицата.',
            'date_of_birth': 'Оставете празно, ако е неизвестна.',
            'photo_url': 'Линк към снимка от досието.',
            'cases': 'Може да е заподозрян по няколко случая.',
        }
        error_messages = {
            'first_name': {
                'required': 'Въведете име.',
                'max_length': 'Името е твърде дълго (максимум %(limit_value)d символа).',
            },
            'last_name': {
                'required': 'Въведете фамилия.',
                'max_length': 'Фамилията е твърде дълга (максимум %(limit_value)d символа).',
            },
            'date_of_birth': {
                'invalid': 'Въведете валидна дата.',
            },
            'photo_url': {
                'invalid': 'Въведете валиден линк.',
            },
        }

    placeholders = {
        'first_name': 'Георги',
        'last_name': 'Димитров',
        'alias': 'Шефа',
        'photo_url': 'https://...',
        'description': 'Висок, с белег над лявата вежда...',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, placeholder in self.placeholders.items():
            self.fields[name].widget.attrs['placeholder'] = placeholder

    def clean_cases(self):
        cases = self.cleaned_data['cases']
        if self.instance.pk:
            blocked = (
                Case.objects
                .filter(evidence__implicates=self.instance)
                .exclude(pk__in=[case.pk for case in cases])
                .distinct()
            )
            if blocked:
                numbers = ', '.join(case.case_number for case in blocked)
                raise ValidationError(
                    f'Не може да махнете заподозрения от {numbers}, защото там има улики срещу него.',
                    code='implicated_in_case',
                )
        return cases


class SuspectFilterForm(StyledFormMixin, forms.Form):
    SORT_CHOICES = (
        ('suspicion', 'Най-подозрителни'),
        ('name', 'Фамилия (А-Я)'),
        ('newest', 'Последно добавени'),
    )
    SORT_ORDERING = {
        'suspicion': ('-suspicion_index', 'last_name', 'first_name'),
        'name': ('last_name', 'first_name'),
        'newest': ('-created_at',),
    }

    q = forms.CharField(
        required=False,
        label='Търсене',
        widget=forms.TextInput(attrs={'placeholder': 'Име, фамилия, прякор...'}),
    )
    case = forms.ModelChoiceField(
        required=False,
        label='Досие',
        queryset=Case.objects.all(),
        empty_label='Всички',
    )
    sort = forms.ChoiceField(
        required=False,
        label='Подреждане',
        choices=SORT_CHOICES,
    )

    def ordering(self):
        sort = self.cleaned_data.get('sort') if self.is_valid() else None
        return self.SORT_ORDERING.get(sort or 'suspicion')


class AlibiForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Alibi
        exclude = ('suspect', 'created_at', 'updated_at')
        widgets = {
            'starts_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'ends_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'location': 'Къде е бил',
            'starts_at': 'От',
            'ends_at': 'До',
            'witness': 'Свидетел',
            'notes': 'Бележки',
        }
        help_texts = {
            'witness': 'Кой може да потвърди алибито.',
            'ends_at': 'Трябва да е след началото.',
        }
        error_messages = {
            'location': {
                'required': 'Посочете къде твърди, че е бил.',
            },
            'starts_at': {
                'required': 'Посочете началото.',
                'invalid': 'Въведете валидни дата и час.',
            },
            'ends_at': {
                'required': 'Посочете края.',
                'invalid': 'Въведете валидни дата и час.',
            },
        }

    placeholders = {
        'location': 'кв. Лозенец, ресторант „Мрежата“',
        'witness': 'Сервитьорката Мария',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, placeholder in self.placeholders.items():
            self.fields[name].widget.attrs['placeholder'] = placeholder
