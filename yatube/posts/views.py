from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Group, Post
from core.utils import query_debugger

LIMIT_POSTS = 10
FIRST_SYMBOL_POST = 30
CACHE_SEC = 20
User = get_user_model()


def index(request):
    template = 'posts/index.html'
    title = 'Последние обновления на сайте'
    posts = Post.objects.prefetch_related('group', 'author')
    paginator = Paginator(posts, LIMIT_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'title': title,
        'page_obj': page_obj,
        'cache_sec': CACHE_SEC,
        'page_number': page_number,
    }
    return render(request, template, context)


@query_debugger
def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.prefetch_related('author')
    paginator = Paginator(posts, LIMIT_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    full_name = user.get_full_name()
    template = 'posts/profile.html'
    title = f'{full_name} профайл пользователя'
    posts = user.posts.select_related('group').filter(author=user)
    paginator = Paginator(posts, LIMIT_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    following = False
    if request.user.is_authenticated:
        following = request.user.follower.filter(author=user).exists()
    context = {
        'title': title,
        'author': user,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related('group', 'author'),
        id=post_id, )
    comments = post.comments.select_related('author')
    form = CommentForm()
    promo = post.text[:FIRST_SYMBOL_POST]
    template = 'posts/post_detail.html'
    context = {
        'title': f'Пост {promo}',
        'post': post,
        'is_author': post.author == request.user,
        'comments': comments,
        'form': form,
    }
    return render(request, template, context)


@login_required()
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
        return redirect(f'/profile/{request.user.username}/')
    return render(request, template, {'form': form})


@login_required()
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(
        Post.objects.select_related('group', 'author'),
        id=post_id,
    )
    if post.author != request.user:
        return redirect(f'/posts/{post_id}/')
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect(f'/posts/{post_id}/')
    context = {
        'form': form,
        'is_edit': True,
        'post_id': post_id,
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect(f'/posts/{post_id}/')


@login_required
def follow_index(request):
    template = 'posts/follow_index.html'
    title = 'Последние обновления на сайте по избранным авторам'
    authors = request.user.follower.values_list('author', flat=True)
    posts = Post.objects.prefetch_related('group', 'author').filter(
        author__in=authors)
    paginator = Paginator(posts, LIMIT_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'title': title,
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    is_follow = request.user.follower.filter(author=author).exists()
    if request.user != author and not is_follow:
        request.user.follower.create(author=author)
    return redirect(f'/profile/{username}/')


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user.follower.filter(author=author).exists():
        request.user.follower.get(author=author).delete()
    return redirect(f'/profile/{username}/')
