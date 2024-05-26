from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView
from django.views.generic.edit import FormMixin, UpdateView

from .filters import CommentPostFilter
from .forms import PostCreateForm, CommentForm
from .models import PostModel, CommentModel, User, CategoryModel


class ConfirmUser(UpdateView):
    model = User
    context_object_name = 'confirm_user'

    def post(self, request, *args, **kwargs):
        if 'code' in request.POST:
            user = User.objects.filter(code=request.POST['code'])
            if user.exists():
                user.update(is_active=True)
                user.update(code=None)
            else:
                return render(self.request, 'account/invalid_code.html')
        return redirect('account_login')


class PostList(ListView):
    model = PostModel
    ordering = '-date_published'
    template_name = 'post_list.html'
    context_object_name = 'post_list'
    paginate_by = 3


class PostCreate(LoginRequiredMixin, CreateView):
    form_class = PostCreateForm
    model = PostModel
    template_name = 'post_create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super(PostCreate, self).form_valid(form)


class PostUpdate(LoginRequiredMixin, UpdateView):
    form_class = PostCreateForm
    model = PostModel
    template_name = 'post_edit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post__author'] = PostModel.objects.get(pk=self.kwargs.get('pk')).author
        return context


class CustomSuccessMessageMixin:
    @property
    def success_msg(self):
        return False

    def form_valid(self, form):
        messages.success(self.request, self.success_msg)
        return super().form_valid(form)

    def get_success_url(self):
        return '%s?id=%s' % (self.success_url, self.object.id)


class PostDetail(CustomSuccessMessageMixin, FormMixin, DetailView):
    model = PostModel
    template_name = 'post.html'
    context_object_name = 'post'
    form_class = CommentForm
    success_msg = 'Отклик успешно создан, ожидайте модерации'

    def get_success_url(self, **kwargs):
        return reverse_lazy('posts', kwargs={'pk': self.get_object().id})

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.post = self.get_object()
        self.object.save()
        return super().form_valid(form)


def update_comment_status(request, pk, type):
    comment = CommentModel.objects.get(pk=pk)

    if type == 'public':
        comment.status = True
        comment.save()
        return redirect('/user_post_comments/')

    elif type == 'delete':
        comment.delete()
        return redirect('/user_post_comments/')


class UserPostsComments(LoginRequiredMixin, ListView):
    model = CommentModel
    ordering = '-created'
    context_object_name = 'comment_list'
    template_name = 'user_post_comments.html'

    def get_queryset(self):
        queryset = CommentModel.objects.filter(post__author_id=self.request.user.pk)
        self.filterset = CommentPostFilter(self.request.GET, queryset, request=self.request.user.pk)
        if self.request.GET:
            return self.filterset.qs
        return CommentModel.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


class CategoryListView(PostList):
    model = PostModel
    template_name = 'category_list.html'
    context_object_name = 'category_post_list'

    def get_queryset(self):
        self.category = get_object_or_404(CategoryModel, id=self.kwargs['pk'])
        queryset = PostModel.objects.filter(category=self.category).order_by('-date_published')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_subscriber'] = self.request.user not in self.category.subscribers.all()
        context['category'] = self.category
        return context


@login_required()
def subscribe(request, pk):
    user = request.user
    category = CategoryModel.objects.get(id=pk)
    category.subscribers.add(user)

    message = 'Вы успешно подписались на рассылку постов категории'

    return render(request, 'subscribe.html', {'category': category, 'message': message})


@login_required()
def unsubscribe(request, pk):
    user = request.user
    category = CategoryModel.objects.get(id=pk)
    category.subscribers.remove(user)

    message = 'Вы успешно отписались от категории'

    return render(request, 'unsubscribe.html', {'category': category, 'message': message})
