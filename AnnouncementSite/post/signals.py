from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from django.template.loader import render_to_string

from django.conf import settings
from .models import PostCategory, PostModel, CommentModel


@receiver(m2m_changed, sender=PostCategory)
def notify_about_new_post(sender, instance, **kwargs):
    if kwargs['action'] == 'post_add':
        notifications_after_post_created(instance.pk)


@shared_task
def notifications_after_post_created(pk):
    post = PostModel.objects.get(pk=pk)
    categories = post.category.all()
    title = post.title
    subscribers_users = []

    for cat in categories:
        subscribers = cat.subscribers.all()
        subscribers_users += [s for s in subscribers]

    for subscriber in subscribers_users:
        html_content = render_to_string(
            'post_created_email.html',
            {
                'username': subscriber.username,
                'text': post.title,
                'link': f'{settings.SITE_URL}/{pk}'
            }
        )

        msg = EmailMultiAlternatives(
            subject=title,
            body='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[subscriber.email],
            )

        msg.attach_alternative(html_content, 'text/html')
        msg.send()


@receiver(post_save, sender=CommentModel)
def notify_about_new_reply(sender, instance, **kwargs):
    user = instance.post.author
    pk = instance.post.pk

    def send_email(reply, title, template, subscribers_email):
        html_mail = render_to_string(
            template,
            {
                'username': user.username,
                'text': reply,
                'link': f'{settings.SITE_URL}/user_post_comments/?post={pk}',
            }
        )

        message = EmailMultiAlternatives(
            subject=title,
            body='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=subscribers_email
        )

        message.attach_alternative(html_mail, 'text/html')
        message.send()

    if kwargs['created']:
        send_email(instance.comment, f'Новый отклик на ваше обьявление: {instance.post.title}',
                   'reply_sendmail_author.html', [user.email])


@receiver(post_save, sender=CommentModel)
def notify_about_true_comment(sender, instance, **kwargs):
    user = instance.user
    status = instance.status
    pk = instance.post.pk

    def send_email(reply, title, template, subscribers_email):
        html_mail = render_to_string(
            template,
            {
                'username': user.username,
                'text': reply,
                'link': f'{settings.SITE_URL}/{pk}',
            }
        )

        message = EmailMultiAlternatives(
            subject=title,
            body='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=subscribers_email
        )

        message.attach_alternative(html_mail, 'text/html')
        message.send()

    if status:
        send_email(instance.comment, f'Ваш отклик опубликован!',
                   'true_comment.html', [user.email])


