from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from flask import request
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View, UpdateView
from django.contrib.auth.decorators import login_required
from .models import Profile
from blog.models import Post, Notification
from django.contrib.auth.models import User




def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}. Please login.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


class ProfileView(View):
    def get(self, request, pk, *args, **kwargs):
        profile = Profile.objects.get(pk=pk)
        user = profile.user
        posts = Post.objects.filter(author=user).order_by('-date_posted')
        
        following = Profile.objects.filter(followers__in=[user])
        num_of_following = len(following)
        followers = profile.followers.all()
        num_of_followers = len(followers)
        
        if len(followers) == 0:
            is_following = False

        for follower in followers:
            if follower == request.user:
                is_following = True
                break
            else:
                is_following = False

        context = {
            'user':user,
            'profile':profile,
            'posts':posts,
            'num_of_following': num_of_following,
            'num_of_followers':num_of_followers,
            'is_following':is_following,
        }

        
        return render(request, 'users/profile.html', context)

def UpdateProfile(request, pk):
    u_form = UserUpdateForm(request.POST, instance=request.user)
    p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
    if u_form.is_valid() and p_form.is_valid():
        u_form.save()
        p_form.save()
        messages.success(request, f'Account updated!')
        return redirect('profile', request.user.profile.pk)
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

        context= {
            'u_form':u_form,
            'p_form':p_form,
        }
    return render(request, 'users/update_profile.html', context)
    


class AddFollower(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        pk = self.kwargs.get('username')
        profile = Profile.objects.get(pk=pk)
        profile.followers.add(request.user)

        notification = Notification.objects.create(notification_type=2, from_user=request.user, to_user=profile.user)
        
        return redirect('profile', pk=profile.pk)

class RemoveFollower(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        pk = self.kwargs.get('username')
        profile = Profile.objects.get(pk=pk)
        profile.followers.remove(request.user)
        
        return redirect('profile', pk=profile.pk)


