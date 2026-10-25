from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Count
from django.urls import reverse

from common.models import TimeStampedModel
from common.validators import validate_not_in_future


class SuspectQuerySet(models.QuerySet):
    def with_suspicion(self):
        return self.annotate(suspicion_index=Count('implicating_evidence', distinct=True))


class Suspect(TimeStampedModel):
    first_name = models.CharField(
        max_length=50,
        verbose_name='Име',
    )
    last_name = models.CharField(
        max_length=50,
        verbose_name='Фамилия',
    )
    alias = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Прякор',
    )
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        validators=[validate_not_in_future],
        verbose_name='Дата на раждане',
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание',
    )
    photo_url = models.URLField(
        blank=True,
        verbose_name='Снимка (URL)',
    )
    cases = models.ManyToManyField(
        'cases.Case',
        blank=True,
        related_name='suspects',
        verbose_name='Досиета',
    )

    objects = SuspectQuerySet.as_manager()

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = 'Заподозрян'
        verbose_name_plural = 'Заподозрени'

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        name = f'{self.first_name} {self.last_name}'
        return f'{name} „{self.alias}“' if self.alias else name

    def get_absolute_url(self):
        return reverse('suspects:detail', kwargs={'pk': self.pk})


class Alibi(TimeStampedModel):
    suspect = models.ForeignKey(
        Suspect,
        on_delete=models.CASCADE,
        related_name='alibis',
        verbose_name='Заподозрян',
    )
    location = models.CharField(
        max_length=150,
        verbose_name='Място',
    )
    starts_at = models.DateTimeField(
        verbose_name='От',
    )
    ends_at = models.DateTimeField(
        verbose_name='До',
    )
    witness = models.CharField(
        max_length=120,
        blank=True,
        verbose_name='Свидетел',
    )
    notes = models.TextField(
        blank=True,
        verbose_name='Бележки',
    )

    class Meta:
        ordering = ['starts_at']
        verbose_name = 'Алиби'
        verbose_name_plural = 'Алибита'

    def __str__(self):
        return f'{self.suspect} @ {self.location}'

    def get_absolute_url(self):
        return self.suspect.get_absolute_url()

    def clean(self):
        super().clean()
        if self.starts_at and self.ends_at and self.ends_at <= self.starts_at:
            raise ValidationError(
                {'ends_at': 'Краят на алибито трябва да е след началото му.'},
                code='invalid_range',
            )
        self._validate_not_contradicting()

    def _validate_not_contradicting(self):
        if not (self.suspect_id and self.starts_at and self.ends_at and self.location):
            return
        conflict = (
            Alibi.objects
            .filter(suspect_id=self.suspect_id)
            .exclude(pk=self.pk)
            .exclude(location__iexact=self.location.strip())
            .filter(starts_at__lt=self.ends_at, ends_at__gt=self.starts_at)
            .first()
        )
        if conflict:
            raise ValidationError(
                f'Алибито противоречи на друго алиби: по същото време заподозряният '
                f'твърди, че е бил в „{conflict.location}“.',
                code='contradicting_alibi',
            )
