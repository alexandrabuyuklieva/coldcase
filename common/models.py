from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Създадено на',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Обновено на',
    )

    class Meta:
        abstract = True
