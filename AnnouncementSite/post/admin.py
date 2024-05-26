from django import forms
from django.contrib import admin
from ckeditor_uploader.widgets import CKEditorUploadingWidget

from .models import PostModel, CategoryModel, CommentModel, User


class PostModelAdminForm(forms.ModelForm):
    content = forms.CharField(label='Описание', widget=CKEditorUploadingWidget ())

    class Meta:
        model = PostModel
        fields = '__all__'


@admin.register(PostModel)
class PostModelAdmin(admin.ModelAdmin):
    form = PostModelAdminForm


admin.site.register(User)
admin.site.register(CommentModel)
admin.site.register(CategoryModel)
