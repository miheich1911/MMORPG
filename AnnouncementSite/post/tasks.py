import datetime

from celery import shared_task
import time

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from .models import PostModel, CategoryModel


@shared_task
def notify_about_new_comment():
    today = datetime.datetime.now()
    last_week = today - datetime.timedelta(days=7)
    posts = PostModel.objects.filter(date_in__gte=last_week)
    categories = set(posts.values_list('category__cat_name', flat=True))
    subscribers = set(CategoryModel.objects.filter(cat_name__in=categories).values_list('subscribers__email', flat=True))

    html_content = render_to_string(
        'flatpages/daily_post.html',
        {
            'link': settings.SITE_URL,
            'posts': posts,
        }
    )

    msg = EmailMultiAlternatives(
        subject='Статьи за неделю',
        body='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=subscribers,
    )

    msg.attach_alternative(html_content, 'text/html')
    msg.send()


