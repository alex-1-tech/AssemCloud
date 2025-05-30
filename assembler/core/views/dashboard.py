"""Dashboard views for the assembler core app."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from core.models import Machine, Task


def get_task_color(task: Task) -> str:
    """Return a hex color code string based on the task's status and priority."""
    if task.status == task.Status.COMPLETED:
        return "#6c757d"
    if task.priority == Task.Priority.HIGH:
        return "#dc3545"
    if task.priority == Task.Priority.MEDIUM:
        return "#ffc107"
    if task.priority == Task.Priority.LOW:
        return "#198754"
    return "#0d6efd"

def dashboard_view(request: HttpRequest) -> HttpResponse:
    """Render the dashboard view with user, machines, tasks, and calendar events."""
    received_tasks = Task.objects.filter(
        recipient=request.user,
        status=Task.Status.IN_PROGRESS,
    ).order_by("due_date")
    sent_tasks = Task.objects.filter(
        sender=request.user,
        status=Task.Status.IN_PROGRESS,
    ).order_by("due_date")
    machines = Machine.objects.all()

    calendar_events = [
        {
            "title": task.title,
            "start": task.due_date.isoformat(),
            "url": f"/tasks/{task.pk}/",
            "color": get_task_color(task),
        }
        for task in received_tasks if task.due_date
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
