from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_year(value):
    now = timezone.now().year
    if value > now:
        raise ValidationError(f'Year: {value} cannot be greater than {now}')
    if value < 0:
        raise ValidationError('Year cannot be negative.')
