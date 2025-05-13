from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from core.models import User


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    pass


account_activation_token = AccountActivationTokenGenerator()


def check_token_uid(uidb64, token):
    """
    Расшифровать uidb64 и проверить токен.
    Вернуть user_id, если всё ок, иначе бросить ошибку.
    """
    user_id = force_str(urlsafe_base64_decode(uidb64))
    if account_activation_token.check_token(User.objects.get(pk=user_id), token):
        return user_id
    from django.core.signing import BadSignature

    raise BadSignature("Неверная пара uid/token")
