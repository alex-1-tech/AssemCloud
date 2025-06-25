"""Dashboard views for the assembler core app."""

from datetime import timedelta

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone

from core.models import Machine, Task


def get_task_color(task: Task) -> str:
    """Return a hex color code string based on the task's status and priority."""
    color = "#0d6efd"  # default
    if task.status == Task.Status.ON_REVIEW:
        color = "#1976d2"  # blue
    elif task.status == Task.Status.ACCEPTED:
        color = "#219653"  # green
    elif task.status == Task.Status.REJECTED:
        color = "#c0392b"  # red
    elif task.status == Task.Status.ABANDONED:
        color = "#6c757d"  # gray
    elif task.priority == Task.Priority.HIGH:
        color = "#dc3545"
    elif task.priority == Task.Priority.MEDIUM:
        color = "#ffc107"
    elif task.priority == Task.Priority.LOW:
        color = "#198754"
    return color


def dashboard_view(request: HttpRequest) -> HttpResponse:
    """Render the dashboard view with user, machines, tasks, and calendar events."""
    seven_days_ago = timezone.now().date() - timedelta(days=7)
    all_reveived_tasks = Task.objects.filter(
        recipient=request.user,
    )
    received_tasks = Task.objects.filter(
        recipient=request.user,
        due_date__gte=seven_days_ago,
    ).order_by("due_date")
    sent_tasks = Task.objects.filter(
        sender=request.user,
        due_date__gte=seven_days_ago,
    ).order_by("due_date")
    machines = Machine.objects.all()

    calendar_events = [
        {
            "title": task.title,
            "start": task.due_date.isoformat(),
            "url": f"/tasks/{task.pk}/",
            "color": get_task_color(task),
        }
        for task in all_reveived_tasks
        if task.due_date
    ]

    return render(
        request,
        "dashboard/index.html",
        {
            "user": request.user,
            "machines": machines,
            "received_tasks": received_tasks,
            "sent_tasks": sent_tasks,
            "calendar_events": calendar_events,
        },
    )
