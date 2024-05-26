from django.urls import path

from .views import PostList, PostCreate, PostDetail, update_comment_status, UserPostsComments, PostUpdate, ConfirmUser, CategoryListView, unsubscribe, subscribe

urlpatterns = [
    path('', PostList.as_view()),
    path('<int:pk>', PostDetail.as_view(), name='posts'),
    path('create/', PostCreate.as_view(), name='post_create'),
    path('<int:pk>/edit', PostUpdate.as_view(), name='post_edit'),
    path('update_comment_status/<int:pk>/<str:type>', update_comment_status, name='update_comment_status'),
    path('user_post_comments/', UserPostsComments.as_view(), name='user_post_comments'),
    path('confirm/', ConfirmUser.as_view(), name='confirm_user'),
    path('categories/<int:pk>', CategoryListView.as_view(), name='category_list'),
    path('categories/<int:pk>/subscribe', subscribe, name='subscribe'),
    path('categories/<int:pk>/unsubscribe', unsubscribe, name='unsubscribe'),
]