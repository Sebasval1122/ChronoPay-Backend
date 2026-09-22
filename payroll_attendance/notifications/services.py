from .models import Notification


def notify(user, type_, message, link=""):
    if user is None:
        return
    Notification.objects.create(recipient=user, type=type_, message=message, link=link)