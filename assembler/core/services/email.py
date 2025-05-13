from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from core.models import User

signer = TimestampSigner()

def send_verification_email(user, request):
    token = signer.sign(user.pk)
    url = request.build_absolute_uri(
        reverse('verify_email', kwargs={'token': token})
    )
    subject = "Подтверждение email"
    message = (
        f"Здравствуйте, {user.first_name}!\n\n"
        "Вы зарегистрировались на нашем сайте. Пожалуйста, подтвердите ваш email, перейдя по ссылке:\n"
        f"{url}\n\n"
        "Если вы не регистрировались — проигнорируйте это письмо."
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

def verify_email(request, token):
    try:
        user_id = signer.unsign(token, max_age=60*24*24)
        user = get_object_or_404(User, pk=user_id)
        user.is_email_verified = True
        user.save()
        messages.success(request, "Email успешно подтвержден.")
    except SignatureExpired:
        messages.error(request, "Срок действия ссылки истёк.")
    except BadSignature:
        messages.error(request, "Неверная ссылка.")
    return redirect('login')
