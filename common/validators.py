from datetime import datetime

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils import timezone
from django.utils.deconstruct import deconstructible


@deconstructible
class NotInFutureValidator:
    message = 'Датата не може да бъде в бъдещето.'
    code = 'future_date'

    def __call__(self, value):
        if isinstance(value, datetime):
            value = timezone.localtime(value).date() if timezone.is_aware(value) else value.date()
        if value > timezone.localdate():
            raise ValidationError(self.message, code=self.code)

    def __eq__(self, other):
        return isinstance(other, NotInFutureValidator)


validate_not_in_future = NotInFutureValidator()

case_number_validator = RegexValidator(
    regex=r'^CC-\d{4}-\d{4}$',
    message='Номерът на досието трябва да е във формат CC-ГГГГ-NNNN.',
    code='invalid_case_number',
)
