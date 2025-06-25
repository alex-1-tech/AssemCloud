"""Telegram bot webhook views for handling user registration and commands."""

import json
import threading
from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from core.models import User
from core.services import send_telegram_message


@csrf_exempt
def telegram_webhook(request: HttpRequest) -> JsonResponse:
    """Handle incoming Telegram webhook requests for registration and commands."""
    data = json.loads(request.body.decode("utf-8"))
    response = JsonResponse({"ok": True})

    def handle() -> None:
        message = data.get("message", {})
        if not message:
            return
        chat_id = message.get("chat", {}).get("id")
        user_id = message.get("from", {}).get("id")
        text = message.get("text", "")
        pending_email = cache.get(f"awaiting_email_{user_id}")
        if text == "/start":
            send_telegram_message(
                "Добро пожаловать! Пожалуйста, введите ваш email для регистрации.",
                chat_id,
            )
            cache.set(f"awaiting_email_{user_id}", value=True, timeout=300)
        elif pending_email:
            try:
                user = User.objects.get(email=text)
                user.telegram_chat_id = str(chat_id)
                user.save()
                send_telegram_message(
                    "✅ Telegram успешно привязан к вашему аккаунту.",
                    chat_id,
                )
            except User.DoesNotExist:
                send_telegram_message(
                    "❌ Пользователь с такой почтой не найден.",
                    chat_id,
                )

            cache.delete(f"awaiting_email_{user_id}")
        else:
            send_telegram_message("⚠️ Неизвестная команда. Введите /start", chat_id)

    threading.Thread(target=handle).start()
    return response


class ToggleTelegramNotificationsView(LoginRequiredMixin, View):
    """Toggle the user's Telegram notification preference."""

    def post(
        self,
        request: HttpRequest,
        *args: tuple[Any, ...],  # noqa: ARG002
        **kwargs: dict[str, Any],  # noqa: ARG002
    ) -> HttpResponse:
        """Mark whether a person wants notifications."""
        user = request.user
        wants_notifications = request.POST.get("wants_telegram_notifications") == "on"
        user.wants_telegram_notifications = wants_notifications
        user.save(update_fields=["wants_telegram_notifications"])
        messages.success(request, "Настройки уведомлений обновлены.")
        return redirect("user_profile", pk=user.pk)

    def get(
        self,
        request: HttpRequest,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> HttpResponse:
        """Allow GET to trigger the same as POST for convenience."""
        return self.post(request, *args, **kwargs)
