from django.contrib.auth.models import AbstractUser
from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField
from django.urls import reverse
from .resourses import post_categories, comment_status


class User(AbstractUser):
    code = models.CharField(max_length=15, blank=True, null=True)


class CategoryModel(models.Model):
    name = models.CharField(max_length=25, unique=True, choices=post_categories)
    subscribers = models.ManyToManyField(User, blank=True, null=True, related_name='categories')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class PostModel(models.Model):
    title = models.CharField(max_length=128, verbose_name='Заголовок')
    content = RichTextUploadingField()
    category = models.ManyToManyField(CategoryModel, through="PostCategory", verbose_name='Категория')
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Автор')
    date_published = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')

    def get_absolute_url(self):
        return reverse('posts', args=[str(self.id)])

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.title


class CommentModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    post = models.ForeignKey(PostModel, on_delete=models.CASCADE,  verbose_name='Пост', related_name='comments')
    comment = models.TextField(verbose_name='Комментарий')
    created = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False, choices=comment_status, verbose_name='Видимость')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'


class PostCategory(models.Model):
    post = models.ForeignKey(PostModel, on_delete=models.CASCADE)
    category = models.ForeignKey(CategoryModel, on_delete=models.CASCADE)
