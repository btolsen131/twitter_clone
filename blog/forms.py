from .models import Comment
from django import forms

class CommentForm(forms.ModelForm):
    comment = forms.CharField(
        label='',
        widget=forms.Textarea(attrs={
            'rows': '3',
            'placeholder' : 'Comment here...'
        })
    )
    class Meta:
        model = Comment
        fields = ['comment']

class ThreadForm(forms.Form):
    username = forms.CharField(label='', max_length=100)

class MessageForm(forms.Form):
    message = forms.CharField(label='', max_length=1000)