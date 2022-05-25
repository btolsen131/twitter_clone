from django.urls import path
from . import views
from .views import PostListView, PostDetailView, PostCreateView, RemoveNotification, PostDeleteView, AddLike, UserSearch, PostNotification, FollowNotification, CommentDeleteView

urlpatterns = [
    path('', PostListView.as_view(), name='blog-home'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/delete', PostDeleteView.as_view(), name='post-delete'),
    path('post/<int:post_pk>/comment/delete/<int:pk>', CommentDeleteView.as_view(), name='comment-delete'),
    path('about/', views.about, name='blog-about'),
    path('like/<int:pk>',AddLike.as_view(), name='like-post'),
    path('search/', UserSearch.as_view(), name="profile-search"),
    path('notification/<int:notification_pk>/post/<int:post_pk>', PostNotification.as_view(),name='post-notification'),
    path('notification/<int:notification_pk>/profile/<int:profile_pk>', FollowNotification.as_view(),name='follow-notification'),
    path('notification/delete/<int:notification_pk>', RemoveNotification.as_view(), name='notification-delete')
]
