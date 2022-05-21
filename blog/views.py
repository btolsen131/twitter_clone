from django.shortcuts import render, get_object_or_404
from flask import request
from .models import Post
from django.views.generic import View, DetailView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import redirect
from users.models import Profile
from django.core.paginator import Paginator
from django.db.models import Q



# def LikeView(request, pk):
#     post = get_object_or_404(Post, id=request.POST.get('post_id'))
#     post.likes.add(request.user)
#     return HttpResponseRedirect(reverse('post-detail', args=[str(pk)]))

class PostListView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        logged_in_user = request.user
        posts = Post.objects.filter(author__profile__followers__in=[logged_in_user]).order_by('-date_posted')
        
        paginator = Paginator(posts, 8)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            
            'page_obj':page_obj
        }
        return render(request, 'blog/home.html', context)

class PostDetailView(DetailView):
    model = Post
    def post(self, request, pk, *args, **kwargs):
        post = Post.object.get(pk=pk)

        is_liked = False
        for like in post.likes.all():
            if like == request.user:
                is_liked = True
                break
        context = {
            'is_liked':is_liked,
        }
        return render(request, 'blog/post_detail.html', context)

    
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'
    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

def about(request):
    return render(request, 'blog/about.html', {'title':'About'})

class AddLike(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)
        
        is_liked = False
        
        for like in post.likes.all():
            if like == request.user:
                is_liked = True
                break
        if not is_liked:
            post.likes.add(request.user)

        if is_liked:
            post.likes.remove(request.user)
        return HttpResponseRedirect(reverse('post-detail', args=[str(pk)]))

class UserSearch(View):
    def get(self, request, * args, **kwargs):
        query = self.request.GET.get('query')
        profile_list = Profile.objects.filter(Q(user__username__icontains=query))

        context =  {
            'profile_list':profile_list
        }

        return render(request, 'blog/search.html', context)


