from django import forms
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin

from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from ckeditor.widgets import CKEditorWidget
from taggit.managers import TaggableManager

from .manager import CustomUserManager


class customUser(AbstractBaseUser,PermissionsMixin):
    email = models.EmailField(verbose_name = 'email address', unique = True)
    username = models.CharField(max_length = 150, null=True)
    is_staff = models. BooleanField(default = False)
    is_active = models. BooleanField(default = True)
    date_joined = models.DateTimeField(default = timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username',]

    objects = CustomUserManager()

    def __str__(self):
        return self.email

class Post(models.Model):
    author = models.ForeignKey(customUser,on_delete=models.CASCADE )
    title = models.CharField(max_length = 200)
    description = models.CharField(max_length = 200)
    tags = TaggableManager()
    text = RichTextUploadingField(blank = True, null = "")
    thumbnail = models.ImageField(upload_to='thumbnails/', null=True, blank=True)
    created_date = models.DateTimeField(default = timezone.now)
    published_date = models.DateTimeField(blank = True, null = True)

    def published(self):
        self.published_date = timezone.now()
        self.save()
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('article', kwargs={'pk': self.pk, 'pt':self.title})

class Comment(models.Model):
    author = models.ForeignKey(customUser,on_delete = models.CASCADE, verbose_name = 'user')
    body = RichTextField(blank = True, null="")
    create_date = models.DateTimeField('time', auto_now_add = True)
    belong = models.ForeignKey(Post, on_delete = models.CASCADE)
    parent = models.ForeignKey("self", on_delete = models.CASCADE, blank = True, null = True, related_name="replies")

    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = verbose_name
        ordering = ['-create_date']