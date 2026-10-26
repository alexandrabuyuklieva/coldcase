from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.urls import reverse

from common.models import TimeStampedModel
from common.validators import validate_not_in_future


class Evidence(TimeStampedModel):
    class EvidenceType(models.TextChoices):
        PHYSICAL = 'physical', 'Веществено'
        DOCUMENT = 'document', 'Документ'
        TESTIMONY = 'testimony', 'Свидетелски показания'
        DIGITAL = 'digital', 'Дигитално'
        FORENSIC = 'forensic', 'Криминалистична експертиза'

    case = models.ForeignKey(
        'cases.Case',
        on_delete=models.CASCADE,
        related_name='evidence',
        verbose_name='Досие',
    )
    title = models.CharField(
        max_length=120,
        verbose_name='Наименование',
    )
    evidence_type = models.CharField(
        max_length=20,
        choices=EvidenceType.choices,
        default=EvidenceType.PHYSICAL,
        verbose_name='Вид',
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание',
    )
    collected_on = models.DateField(
        validators=[validate_not_in_future],
        verbose_name='Дата на откриване',
    )
    found_at = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Място на откриване',
    )
    confidence = models.PositiveSmallIntegerField(
        default=50,
        validators=[
            MinValueValidator(0, message='Достоверността не може да е под %(limit_value)s%%.'),
            MaxValueValidator(100, message='Достоверността не може да е над %(limit_value)s%%.'),
        ],
        verbose_name='Достоверност (%)',
    )
    implicates = models.ForeignKey(
        'suspects.Suspect',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='implicating_evidence',
        verbose_name='Уличава',
    )

    class Meta:
        ordering = ['-collected_on', '-created_at']
        verbose_name = 'Улика'
        verbose_name_plural = 'Улики'
        constraints = [
            models.CheckConstraint(
                condition=Q(confidence__lte=100),
                name='evidence_confidence_max_100',
                violation_error_message='Достоверността не може да е над 100%.',
            ),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('evidence:detail', kwargs={'pk': self.pk})

    def clean(self):
        super().clean()
        errors = {}
        if self.case_id and self.collected_on and self.collected_on < self.case.crime_date:
            errors['collected_on'] = ValidationError(
                f'Уликата не може да е открита преди престъплението '
                f'({self.case.crime_date:%d.%m.%Y}).',
                code='before_crime',
            )
        if self.case_id and self.implicates_id and not self.case.suspects.filter(pk=self.implicates_id).exists():
            errors['implicates'] = ValidationError(
                'Заподозреният не е свързан с това досие.',
                code='suspect_not_in_case',
            )
        if errors:
            raise ValidationError(errors)
