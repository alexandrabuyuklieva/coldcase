from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone

from common.models import TimeStampedModel
from common.validators import case_number_validator, validate_not_in_future


class Case(TimeStampedModel):
    class Status(models.TextChoices):
        OPEN = 'open', 'Открит'
        SOLVED = 'solved', 'Разкрит'
        FROZEN = 'frozen', 'Замразен'

    CASE_NUMBER_PREFIX = 'CC'

    case_number = models.CharField(
        max_length=12,
        unique=True,
        editable=False,
        validators=[case_number_validator],
        verbose_name='Номер на досието',
    )
    title = models.CharField(
        max_length=120,
        verbose_name='Заглавие',
    )
    description = models.TextField(
        verbose_name='Описание',
    )
    crime_date = models.DateField(
        validators=[validate_not_in_future],
        verbose_name='Дата на престъплението',
    )
    location = models.CharField(
        max_length=150,
        verbose_name='Място',
    )
    victim = models.CharField(
        max_length=120,
        blank=True,
        verbose_name='Жертва',
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.OPEN,
        verbose_name='Статус',
    )

    class Meta:
        ordering = ['-crime_date', '-created_at']
        verbose_name = 'Досие'
        verbose_name_plural = 'Досиета'

    def __str__(self):
        return f'{self.case_number} · {self.title}'

    def get_absolute_url(self):
        return reverse('cases:detail', kwargs={'pk': self.pk})

    def clean(self):
        super().clean()
        if self.pk and self.crime_date and self.evidence.filter(collected_on__lt=self.crime_date).exists():
            raise ValidationError(
                {'crime_date': 'Има улики, открити преди тази дата. Коригирайте първо тях.'},
                code='evidence_before_crime',
            )

    def save(self, *args, **kwargs):
        if not self.case_number:
            self.case_number = self._generate_case_number()
        super().save(*args, **kwargs)

    @classmethod
    def _generate_case_number(cls):
        prefix = f'{cls.CASE_NUMBER_PREFIX}-{timezone.localdate().year}-'
        last_number = (
            cls.objects
            .filter(case_number__startswith=prefix)
            .order_by('-case_number')
            .values_list('case_number', flat=True)
            .first()
        )
        sequence = int(last_number.rsplit('-', 1)[1]) + 1 if last_number else 1
        return f'{prefix}{sequence:04d}'
