import re

from django.core.exceptions import ValidationError


def validate_username(value):
    reg = re.compile(r'^[\w.@+-]+$')
    if not reg.match(value):
        raise ValidationError(
            'Username содержит недопустимые символы!',
            params={'value': value},
        )
    if value == 'me':
        raise ValidationError(
            '\"me\". Такое имя пользователя запрещено к использованию.',
            params={'value': value},
        )
