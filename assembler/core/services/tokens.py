"""Module for account activation token generation and verification.

Provides functionality to decode user ID from base64 and verify
the activation token for user account activation.
"""

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.signing import BadSignature
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from core.models import User


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    """Token generator for account activation."""


account_activation_token = AccountActivationTokenGenerator()


def check_token_uid(uidb64: str, token: str) -> str:
    """Decode uidb64 and check the token."""
    user_id = force_str(urlsafe_base64_decode(uidb64))
    user = User.objects.get(pk=user_id)
    if account_activation_token.check_token(user, token):
        return user_id

    msg = "Invalid uid/token pair"
    raise BadSignature(msg)
