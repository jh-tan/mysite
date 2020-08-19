import random
from django import forms
from datetime import datetime
from taggit.models import Tag
from .forms import createPost,createComment
from .models import customUser,Post,Comment
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django.db import IntegrityError
from django.views.generic.dates import ArchiveIndexView
from django.contrib.auth import authenticate,login,logout
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect,get_object_or_404
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage


def register(response):
    if response.method == 'POST':
        try:
            return render(response,"blog/close.html")
        except IntegrityError :
            return render(response,"blog/close.html")
        except ValueError:
            return render(response,"blog/close.html")
    return render(response,"blog/signin.html")

def user_login(request):
    if request.method == "POST":
        username = request.POST['username'] 
        password = request.POST['password']
        user = authenticate(request, email=username, password=password) or authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            request.session.set_expiry(1800)
            return redirect('/')
    return render(request, 'blog/signin.html')

def user_logout(request):
    logout(request)
    return redirect('/')

def home(response):
    current=response.user
    most_common = Post.tags.most_common()[:10]
    query=response.GET.get("q")
    if query:
        return search_post(response,query)
    else:
        post_list = Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
        p = Paginator(post_list,5)
        page_number=response.GET.get('page')
        try:
            posts=p.page(page_number)
        except PageNotAnInteger:
            posts=p.page(1)
        except EmptyPage:
            posts=p.page(p.num_pages)

        page_obj=p.get_page(page_number)
        carousel_obj=get_carousel(Post)
        
        if carousel_obj:
            hasCarousel=True
            context= {
                'posts':posts,'curr':current,'page_obj':page_obj,
                'common':most_common,'img1':Post.objects.get(pk=carousel_obj[0]),'img2':Post.objects.get(pk=carousel_obj[1])
                ,'img3':Post.objects.get(pk=carousel_obj[2]),'hasCarousel':hasCarousel
            }
        else:
            hasCarousel=False
            context= {
                'posts':posts,'curr':current,'page_obj':page_obj,
                'common':most_common,'hasCarousel':hasCarousel
            }
        return render(response,"blog/home.html",context)

def create(response):
    admin=response.user
    if response.method == 'POST':
        create = createPost(response.POST,response.FILES)
        if create.is_valid():
            post=Post(author=admin,title=create.cleaned_data["title"],text=create.cleaned_data["text"],
            description=create.cleaned_data["description"],thumbnail=create.cleaned_data['thumbnail'])
            post.save()
            post.tags.add(*create.cleaned_data["tags"])
            post.published()
            return redirect('/')
    else:
        create = createPost()
    return render(response,"blog/create.html",{'form':create,'custom':"Create"})
    
def post_view(response,pk,pt):
    post = get_object_or_404(Post, pk=pk)
    cmt_list = Comment.objects.filter(belong = post.pk, parent__isnull=True)
    if response.method =='GET':
        create = createComment()
        return render(response,"blog/article.html",{'post':post,'cmt_list':cmt_list,'form':create})
    elif response.method == 'POST':
        replies=response.POST.get("rep") 
        create = createComment(response.POST)
        if replies:
            parent_obj = None
            try:
                parent_id = int(response.POST.get('parent_id'))
            except:
                parent_id = None

            if parent_id:
                parent_obj = Comment.objects.get(id = parent_id)
                if parent_obj:
                    comment=Comment(author=response.user, belong = post , body=replies, parent=parent_obj)
                    comment.save()
                    return HttpResponseRedirect(post.get_absolute_url())
        if create.is_valid():
            cmt_user = response.user                       
            cmt_articleid = post.pk     
            cmt_body = create.cleaned_data["text"]
            comment = Comment(author = cmt_user , belong = post, body = cmt_body)
            comment.save()
            return HttpResponseRedirect(post.get_absolute_url())
    else:
        create=createComment()
    return render(response,"blog/article.html",{'post':post,'cmt_list':cmt_list,'form':create})

def tagged(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    # Filter posts by tag name  
    posts = Post.objects.filter(tags=tag)
    carousel_obj=get_carousel(Post)
    most_common = Post.tags.most_common()[:10]
    context = {
        'tag':tag,
        'posts':posts,
        'img1':Post.objects.get(pk=carousel_obj[0]),
        'img2':Post.objects.get(pk=carousel_obj[1]),
        'img3':Post.objects.get(pk=carousel_obj[2]),
        'common':most_common
    }
    query=request.GET.get("q")
    if query:
        return search_post(request,query)
    return render(request, 'blog/home.html', context)

def get_carousel(Post):
    li=[]
    if(Post.objects.count()<3):
        return False
    while True:
        try:
            number=random.randint(int(Post.objects.first().pk),int(Post.objects.last().pk))
            post=Post.objects.get(pk=number)
            if number not in li:
                li.append(number)
        except:
            continue
        if len(li)==3:
            return li
    return False

def post_edit(request,pk,pt=None):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form =createPost(request.POST,request.FILES,instance=post)
        if form.is_valid():
            post.author = request.user
            post.tags.set(*form.cleaned_data["tags"],clear=False)
            post.published()
            return redirect('home')
    else:
        form = createPost(instance=post)
    return render(request, 'blog/create.html', {'form': form,'custom':"Edit"})

def post_delete(response,pk,pt=None):
    post = get_object_or_404(Post,pk=pk)
    if response.method == 'POST':
        form=createPost(response.POST,instance=post)
        form.set_disable(instance=post)
        post.delete()
        return redirect('home')
    else:
        form = createPost(instance=post)
        form.set_disable(instance=post)
    return render(response,'blog/create.html',{'form':form,'custom':"Delete"})

def search_post(response,word):
    most_common = Post.tags.most_common()[:10]
    user=customUser.objects.all()
    posts=Post.objects.filter(Q(title__icontains=word)|
    Q(text__icontains=word)|Q(author__username__icontains=word)).order_by('-published_date')
    carousel_obj=get_carousel(Post)
    context = {
    'posts':posts,
    'img1':Post.objects.get(pk=carousel_obj[0]),
    'img2':Post.objects.get(pk=carousel_obj[1]),
    'img3':Post.objects.get(pk=carousel_obj[2]),
    'common':most_common
    }
    return render(response,"blog/home.html",context)

def archive_list(response):
    post=Post.objects.all()

class ArchiveView(ArchiveIndexView):
    model = Post
    context_object_name = 'posts'
    template_name = 'blog/archive.html'
    date_field = "published_date"



