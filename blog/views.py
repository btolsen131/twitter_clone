import profile
from venv import create
from django.shortcuts import render, get_object_or_404
from flask import request
from .models import Notification, Post, Comment, Thread, MessageModel
from django.views.generic import View, DetailView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect
from users.models import Profile
from django.core.paginator import Paginator
from .forms import CommentForm, ThreadForm, MessageForm
from django.db.models import Q
from django.contrib import messages


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

class PostDetailView(View):
    
    def get(self, request, pk, *arks, **kwargs):
        post = Post.objects.get(pk=pk)
        form = CommentForm()

        comments = Comment.objects.filter(post=post).order_by('-created_on')

        context = {
            'post':post,
            'form':form,
            'comments':comments
        }

        return render(request, 'blog/post_detail.html', context)

    def post(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)

        form = CommentForm(request.POST)

        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.author = request.user
            new_comment.post = post
            new_comment.save()

        comments = Comment.objects.filter(post=post).order_by('-created_on')

        notification = Notification.objects.create(notification_type=3, from_user=request.user, to_user=post.author, post=post)
       
        context = {
            'post':post,
            'comments':comments
        }
        
        return render(request, 'blog/post_detail.html', context)

class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment_confirm_delete.html'

    def get_success_url(self):
        pk = self.kwargs['post_pk']
        return reverse_lazy('post-detail', kwargs={'pk':pk})

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('blog-home')
    template_name = 'blog/post_confirm_delete.html'

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
            notification = Notification.objects.create(notification_type=1, from_user=request.user, to_user=post.author, post=post)

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

class PostNotification(View):
    def get(self, request, notification_pk, post_pk, *args, **kwargs):
        notification = Notification.objects.get(pk=notification_pk)
        post = Post.objects.get(pk=post_pk)

        notification.user_has_seen = True
        notification.save()
        
        return redirect('post-detail', pk=post_pk)

class FollowNotification(View):
    def get(self, request, notification_pk, profile_pk, *args, **kwargs):
        notification = Notification.objects.get(pk=notification_pk)
        profile = Profile.objects.get(pk=profile_pk)
        
        notification.user_has_seen = True
        notification.save()
        
        return redirect('profile', pk=profile_pk)

class RemoveNotification(View):
    def delete(self, request, notification_pk, *args, **kwargs):
        notification = Notification.objects.get(pk=notification_pk)

        notification.user_has_seen = True
        notification.save()
        
        return HttpResponse('Success', context_type='text/plain')

class ListThreads(View):
    def get(self, request, *args, **kwargs):
        threads = Thread.objects.filter(Q(user = request.user) | Q(receiver=request.user))

        context = {
            'threads':threads
        }

        return render(request, 'blog/inbox.html', context)

class CreateThread(View):
    def get(self, request, *args, **kwargs):
        form = ThreadForm()

        context = {
            'form':form
        }

        return render(request, 'blog/create_thread.html', context)
    
    def post(self, request, *args, **kwargs):
        form = ThreadForm(request.POST)

        username = request.POST.get('username')

        try:
            receiver = User.objects.get(username=username)
            if Thread.objects.filter(user=request.user, receiver=receiver).exists():
                thread = Thread.objects.filter(user=request.user, receiver=receiver)[0]
                return redirect('thread', pk=thread.pk)
            elif Thread.objects.filter(user=receiver, receiver=request.user).exists():
                thread = Thread.objects.filter(user=receiver, receiver=request.user)[0]
                return redirect('thread', pk=thread.pk)
            
            if form.is_valid():
                thread = Thread(
                    user=request.user,
                    receiver = receiver
                )
                thread.save()
                return redirect('thread', pk=thread.pk) 
        except:
            messages.warning(request, 'User not found.')
            return redirect('create-thread')

class ThreadView(View):
    def get(self, request, pk, *args, **kwargs):
        form = MessageForm()
        thread = Thread.objects.get(pk=pk)
        message_list = MessageModel.objects.filter(thread__pk__contains=pk)
        context = {
            'thread':thread,
            'form':form,
            'message_list':message_list
        }
        return render(request, 'blog/thread.html', context)

class CreateMessage(View):
    def post(self, request, pk, *args, **kwargs):
        thread = Thread.objects.get(pk=pk)
        if thread.receiver == request.user:
            receiver = thread.user
        else:
            receiver = thread.receiver

        message = MessageModel(
            thread = thread,
            sender_user=request.user,
            receiver_user=receiver,
            body=request.POST.get('message')
        )

        message.save()
        
        return redirect('thread', pk=pk) 