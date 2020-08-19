from django import forms
from .models import customUser,Post,Comment
from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = customUser
        fields = ('email','username',)
    
class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = customUser
        fields = ('email','username',)

class createPost(forms.ModelForm):
    title = forms.CharField(max_length=200)
    description = forms.CharField(widget = forms.Textarea, required=False, max_length=200)
    text = forms.CharField(widget = CKEditorUploadingWidget())
    thumbnail = forms.ImageField(required=False)

    def __init__(self, *args, **kwargs):
        super(createPost, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class' : 'titleclass'})
        self.fields['description'].widget.attrs.update({'class' : 'descriptionclass'})
        self.fields['text'].widget.attrs.update({'class' : 'textclass'})
    
    def set_disable(self,*args,**kwargs):
        super(createPost,self).__init__(*args,**kwargs)
        self.fields['title'].disabled=True
        self.fields['text'].disabled=True
        self.fields['description'].disabled=True
        self.fields['tags'].disabled=True

    class Meta:
        model=Post
        fields=['title','tags','description','thumbnail','text']
        labels = {
            "title":"titleclass",
            "description":"descriptionclass"
        }

class createComment(forms.ModelForm):
    text=forms.CharField(widget = CKEditorWidget(), label = False)

    class Meta:
        model=Comment
        fields=('text',)
        