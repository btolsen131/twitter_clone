from django.urls import path
from . import views
from .views import PostListView, PostDetailView, PostCreateView, PostDeleteView, LikeView, AddLike

urlpatterns = [
    path('', PostListView.as_view(), name='blog-home'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('post/<int:id>/delete', PostDeleteView.as_view(), name='post-delete'),
    path('about/', views.about, name='blog-about'),
    path('like/<int:pk>',AddLike.as_view(), name='like_post'),

]
