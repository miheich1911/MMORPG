from django_filters import FilterSet, ModelChoiceFilter

from post.models import PostModel, CommentModel


class CommentPostFilter(FilterSet):

    class Meta:
        model = CommentModel
        fields = ['post',]
        labels = {
            'post': 'post.title',
        }

    def __init__(self, *args, **kwargs):
        super(CommentPostFilter, self).__init__(*args, **kwargs)
        self.filters['post'].queryset = PostModel.objects.filter(author_id=kwargs['request'])
