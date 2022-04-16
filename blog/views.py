from django.shortcuts import render

posts = [
    {
        'author':'brian',
        'title': 'blog post 1',
        'content':'first post content',
        'date_posted':'april 16'
    },
    {
        'author':'jane',
        'title': 'blog post 2',
        'content':'second post content',
        'date_posted':'april 17'
    },
]


def home(request):
    context = {
        'posts':posts
    }
    return render(request, 'blog/home.html', context) 

def about(request):
    return render(request, 'blog/about.html', {'title':'About'})
