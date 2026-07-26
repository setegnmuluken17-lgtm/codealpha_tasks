from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.utils import timezone
from .models import Post, Like, Comment, Story, StoryLike, StoryView
from accounts.models import Follow
from .forms import PostForm, CommentForm, StoryForm


def active_stories_queryset():
    return Story.objects.filter(expires_at__gt=timezone.now()).select_related('author', 'author__profile')


@login_required(login_url='login')
def feed(request):
    """Display the news feed for logged-in user"""
    user = request.user
    
    # Get posts from users that the current user follows
    following_users = Follow.objects.filter(follower=user).values_list('following_id', flat=True)
    
    # Include user's own posts and posts from followers
    posts = Post.objects.filter(
        Q(author=user) | Q(author_id__in=following_users)
    ).select_related('author', 'author__profile').prefetch_related('likes', 'comments').order_by('-created_at')
    
    # Add like status for current user to each post
    for post in posts:
        post.user_liked = post.likes.filter(user=user).exists()
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = user
            post.save()
            messages.success(request, 'Post created successfully!')
            return redirect('feed')
    else:
        form = PostForm()
    
    context = {
        'form': form,
        'posts': posts,
        'stories': active_stories_queryset(),
    }
    
    return render(request, 'posts/feed.html', context)


@login_required(login_url='login')
def create_post(request):
    """Create a new post"""
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Post created successfully!')
            return redirect('feed')
    else:
        form = PostForm()
    
    return render(request, 'posts/create_post.html', {'form': form})


@login_required(login_url='login')
def post_detail(request, post_id):
    """View detailed post with comments"""
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all().select_related('author', 'author__profile').order_by('-created_at')
    user_liked = False
    
    if request.user.is_authenticated:
        user_liked = post.likes.filter(user=request.user).exists()
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'You must be logged in to comment.')
            return redirect('login')
        
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Comment added successfully!')
            return redirect('post_detail', post_id=post.id)
    else:
        form = CommentForm()
    
    context = {
        'post': post,
        'comments': comments,
        'form': form,
        'user_liked': user_liked,
    }
    
    return render(request, 'posts/post_detail.html', context)


@login_required(login_url='login')
def create_story(request):
    """Create a story that expires after 24 hours."""
    if request.method == 'POST':
        form = StoryForm(request.POST, request.FILES)
        if form.is_valid():
            story = form.save(commit=False)
            story.author = request.user
            story.save()
            messages.success(request, 'Story posted successfully! It will expire in 24 hours.')
            return redirect('feed')
    else:
        form = StoryForm()

    return render(request, 'posts/create_story.html', {'form': form})


def story_detail(request, story_id):
    """Show an active story."""
    story = get_object_or_404(active_stories_queryset(), id=story_id)

    user_liked = False
    viewers = StoryView.objects.none()
    story_likes = StoryLike.objects.none()

    if request.user.is_authenticated:
        if request.user != story.author:
            StoryView.objects.get_or_create(story=story, user=request.user)
        user_liked = story.likes.filter(user=request.user).exists()

        if request.user == story.author:
            viewers = story.views.select_related('user', 'user__profile')
            story_likes = story.likes.select_related('user', 'user__profile')

    return render(request, 'posts/story_detail.html', {
        'story': story,
        'user_liked': user_liked,
        'viewers': viewers,
        'story_likes': story_likes,
    })


@login_required(login_url='login')
def like_story(request, story_id):
    """Like or unlike a story."""
    story = get_object_or_404(active_stories_queryset(), id=story_id)

    like, created = StoryLike.objects.get_or_create(story=story, user=request.user)
    if created:
        messages.success(request, 'Story liked!')
    else:
        like.delete()
        messages.info(request, 'Story unliked.')

    return redirect('story_detail', story_id=story.id)


@login_required(login_url='login')
def delete_story(request, story_id):
    """Delete your own story."""
    story = get_object_or_404(Story, id=story_id)

    if request.user != story.author:
        messages.error(request, 'You can only delete your own stories.')
        return redirect('story_detail', story_id=story.id)

    if request.method == 'POST':
        story.delete()
        messages.success(request, 'Story deleted successfully!')
        return redirect('feed')

    return render(request, 'posts/delete_story.html', {'story': story})


@login_required(login_url='login')
def like_post(request, post_id):
    """Like/Unlike a post"""
    post = get_object_or_404(Post, id=post_id)
    
    like, created = Like.objects.get_or_create(post=post, user=request.user)
    
    if not created:
        like.delete()
        liked = False
        messages.info(request, 'Post unliked.')
    else:
        liked = True
        messages.success(request, 'Post liked!')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'liked': liked,
            'like_count': post.likes.count()
        })
    
    return redirect('post_detail', post_id=post.id)


@login_required(login_url='login')
def delete_post(request, post_id):
    """Delete a post"""
    post = get_object_or_404(Post, id=post_id)
    
    if request.user != post.author:
        messages.error(request, 'You can only delete your own posts.')
        return redirect('post_detail', post_id=post.id)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted successfully!')
        return redirect('feed')
    
    return render(request, 'posts/delete_post.html', {'post': post})


@login_required(login_url='login')
def delete_comment(request, comment_id):
    """Delete a comment"""
    comment = get_object_or_404(Comment, id=comment_id)
    post = comment.post
    
    if request.user != comment.author:
        messages.error(request, 'You can only delete your own comments.')
        return redirect('post_detail', post_id=post.id)
    
    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'Comment deleted successfully!')
        return redirect('post_detail', post_id=post.id)
    
    return render(request, 'posts/delete_comment.html', {'comment': comment})


@login_required(login_url='login')
def edit_post(request, post_id):
    """Edit a post"""
    post = get_object_or_404(Post, id=post_id)
    
    if request.user != post.author:
        messages.error(request, 'You can only edit your own posts.')
        return redirect('post_detail', post_id=post.id)
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            if form.cleaned_data.get('remove_video'):
                post.video = None
            post.save()
            messages.success(request, 'Post updated successfully!')
            return redirect('post_detail', post_id=post.id)
    else:
        form = PostForm(instance=post)
    
    return render(request, 'posts/edit_post.html', {'form': form, 'post': post})


def explore(request):
    """Explore all posts (for anonymous and authenticated users)"""
    posts = Post.objects.all().select_related('author', 'author__profile').prefetch_related('likes', 'comments').order_by('-created_at')
    
    # Add like status for current user to each post (if authenticated)
    if request.user.is_authenticated:
        for post in posts:
            post.user_liked = post.likes.filter(user=request.user).exists()
    
    context = {
        'posts': posts,
        'stories': active_stories_queryset(),
    }
    
    return render(request, 'posts/explore.html', context)

