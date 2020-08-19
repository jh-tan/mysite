from django.urls import path,re_path,include
from django.views.generic import TemplateView 
from . import views

urlpatterns = [
    path('', views.home, name = 'home'),
    path('signin/',views.user_login, name = 'login'),
    path('signin/register/',views.register, name = 'register'),
    path('logout/',views.user_logout, name = 'user_logout'),
    path('create/', views.create, name = 'create'),
    path('tag/<slug:slug>/', views.tagged, name="tagged"),
    re_path(r'^post/(?P<pk>[0-9]+)/(?P<pt>[\w-]+/?)', views.post_view, name='article'),
    re_path(r'^edit_post/(?P<pk>[0-9]+)/(?P<pt>[\w-]+/?)', views.post_edit, name='edit'),
    re_path(r'^delete_post/(?P<pk>[0-9]+)/(?P<pt>[\w-]+/?)', views.post_delete, name='delete'),
    re_path(r'^tag/([\w]+)/', views.home, name='query'),
    re_path(r'^archive/$', views.ArchiveView.as_view(), name='archive'),
    path('accounts/', include('allauth.urls')),

]