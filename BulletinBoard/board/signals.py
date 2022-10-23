from django.contrib import auth
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Comment, Bulletin
from django.core.mail import send_mail


@receiver(post_save, sender=Comment)
def send_mail_resp(instance, created):
    if created:
        user = Bulletin.objects.get(pk=instance.post_id).user
        send_mail(
            subject='Новый отклик',
            message=f'{instance.date_added.strftime("%d %m %Y")} - {instance.body [:50]}',
            from_email='',
            recipient_list=[auth.email]
        )
