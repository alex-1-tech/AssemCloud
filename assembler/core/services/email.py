"""Module for sending verification emails and verifying user email addresses.

Includes functions to send verification emails with activation tokens
and to verify users based on token and UID from URL parameters.
"""

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.core.signing import BadSignature, SignatureExpired
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from core.models import User

from .tokens import account_activation_token as signer
from .tokens import check_token_uid


def send_verification_email(user: User, request: HttpRequest) -> None:
    """Send an email to the user with a verification link."""
    token = signer.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    url = request.build_absolute_uri(
        reverse("verify_email", kwargs={"uidb64": uid, "token": token}),
    )
    subject = "Email Verification"
    message = (
        f"Hello, {user.first_name}!\n\n"
        "You have registered on our site. "
        "Please verify your email by clicking the link below:\n"
        f"{url}\n\n"
        "If you did not register, please ignore this email."
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])


def verify_email(request: HttpRequest, uidb64: str, token: str) -> HttpResponse:
    """Verify the user's email address using uidb64 and token."""
    try:
        user_id = check_token_uid(uidb64, token)
        user = get_object_or_404(User, pk=user_id)
        user.is_email_verified = True
        user.save()
        messages.success(request, "Email successfully verified.")
    except SignatureExpired:
        messages.error(request, "The verification link has expired.")
    except BadSignature:
        messages.error(request, "Invalid verification link.")
    return redirect("login")
