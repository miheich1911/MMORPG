import random

from allauth.account.forms import SignupForm
from django import forms
from django.conf import settings
from django.core.mail import send_mail
from django.forms import TextInput
from .resourses import gender
from string import hexdigits

from .models import PostModel, CommentModel
from ckeditor_uploader.widgets import CKEditorUploadingWidget


class PostCreateForm(forms.ModelForm):
    content = forms.CharField(label='Описание', widget=CKEditorUploadingWidget())

    class Meta:
        model = PostModel
        fields = ['title', 'category','content']
        widgets = {
            "title": TextInput(attrs={"class": "text"}),
        }

        labels = {
            'title': 'Заголовок',
            'category': 'Категория'
        }


class CommentForm(forms.ModelForm):
    comment = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "placeholder": "Введите текст комментария",
                "rows": 2
            }
        ),
    )

    class Meta:
        model = CommentModel
        fields = ("comment",)


class CommonSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label='Имя')
    last_name = forms.CharField(max_length=30, label='Фамилия')

    def signup(self, request, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()

    def save(self, request):
        user = super(CommonSignupForm, self).save(request)
        user.is_active = False
        code = ''.join(random.sample(hexdigits, 5))
        user.code = code
        user.save()
        send_mail(
            subject=f'Код активации',
            message=f'Код активации аккаунта: {code}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )
        return user
