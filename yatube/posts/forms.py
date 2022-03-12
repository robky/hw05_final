from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    def clean_text(self):
        data = self.cleaned_data['text']
        if data == '':
            raise forms.ValidationError('А кто поле будет заполнять, Пушкин?')
        return data

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text', )
