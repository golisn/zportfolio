from .models import Comment
from django import forms

class CommentForm(forms.ModelForm):
    class Meta:
        template_name = '/alpha/commucreate.html'
        model = Comment
        fields = ('content',)