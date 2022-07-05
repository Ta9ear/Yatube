from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Group, Post, User
from .utils import paginate


@cache_page(20, key_prefix="index_page")
def index(request):
    """
    Function rendering html template and returning
    model objects and limits according to paginator for main page
    """
    posts_list = Post.objects.select_related('group', 'author')
    page_obj = paginate(posts_list, request)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """
    Function rendering html template and returning
    model objects and limits according to paginator for group posts page
    """
    group = get_object_or_404(Group, slug=slug)
    posts_list = group.posts.select_related('group', 'author')
    page_obj = paginate(posts_list, request)
    context = {
        'page_obj': page_obj,
        'group': group,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """
    Function rendering html template and returning
    model objects
    """
    author = get_object_or_404(User, username=username)
    post_list = author.posts.select_related('group', 'author')
    page_obj = paginate(post_list, request)
    context = {
        'author': author,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """
    Function rendering html template and returning
    model objects
    """
    post_object = get_object_or_404(Post.objects.select_related(
        'group',
        'author',
    ), id=post_id)
    comments = post_object.comments.select_related('author', 'post')
    form = CommentForm(request.POST or None)
    context = {
        'post_object': post_object,
        'comments': comments,
        'form': form
    }
    return render(
        request,
        'posts/post_detail.html',
        context
    )


@login_required
def post_create(request):
    """
    Function rendering html template and returning
    model objects
    """
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if request.method == "POST" and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()
        return redirect('posts:profile', username=post.author)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    """
    Function rendering html template and returning
    model objects
    """
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    return render(
        request,
        'posts/create_post.html',
        {'form': form, 'is_edit': True}
    )


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post.objects.select_related(
        'author',
        'group',
    ), id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)
