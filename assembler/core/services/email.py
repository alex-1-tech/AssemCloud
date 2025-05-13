from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.core.signing import BadSignature, SignatureExpired
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from core.models import User

from .tokens import account_activation_token as signer
from .tokens import check_token_uid


def send_verification_email(user, request):
    token = signer.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    url = request.build_absolute_uri(
        reverse("verify_email", kwargs={"uidb64": uid, "token": token})
    )
    subject = "Подтверждение email"
    message = (
        f"Здравствуйте, {user.first_name}!\n\n"
        "Вы зарегистрировались на нашем сайте."
        " Пожалуйста, подтвердите ваш email, перейдя по ссылке:\n"
        f"{url}\n\n"
        "Если вы не регистрировались — проигнорируйте это письмо."
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])


def verify_email(request, uidb64, token):
    try:
        user_id = check_token_uid(uidb64, token)
        user = get_object_or_404(User, pk=user_id)
        user.is_email_verified = True
        user.save()
        messages.success(request, "Email успешно подтвержден.")
    except SignatureExpired:
        messages.error(request, "Срок действия ссылки истёк.")
    except BadSignature:
        messages.error(request, "Неверная ссылка.")
    return redirect("login")
