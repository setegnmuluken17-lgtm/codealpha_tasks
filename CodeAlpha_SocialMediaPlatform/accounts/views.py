from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone

from .models import UserProfile, Follow
from .forms import RegistrationForm, LoginForm, UserProfileForm
from posts.models import Post, Story


def register(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('profile', username=request.user.username)
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to SocialHub, {user.username}!')
            return redirect('feed')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = RegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('profile', username=request.user.username)
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me')
            
            user = authenticate(request, username=username, password=password)
            if user is None:
                user = authenticate(request, username__iexact=User.objects.filter(email=username).values_list('username', flat=True).first(), password=password)
            
            if user is not None:
                login(request, user)
                if not remember_me:
                    request.session.set_expiry(0)
                messages.success(request, f'Welcome back, {user.username}!')
                next_url = request.GET.get('next', 'feed')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


@login_required(login_url='login')
def profile(request, username):
    """View user profile"""
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(UserProfile, user=user)
    posts = Post.objects.filter(author=user)
    stories = Story.objects.filter(author=user, expires_at__gt=timezone.now()).select_related('author', 'author__profile')
    followers_count = Follow.objects.filter(following=user).count()
    following_count = Follow.objects.filter(follower=user).count()
    
    is_following = False
    can_message = False
    if request.user.is_authenticated and request.user != user:
        is_following = Follow.objects.filter(follower=request.user, following=user).exists()
        can_message = is_following and Follow.objects.filter(follower=user, following=request.user).exists()
    
    context = {
        'user': user,
        'profile': profile,
        'posts': posts,
        'stories': stories,
        'followers_count': followers_count,
        'following_count': following_count,
        'is_following': is_following,
        'can_message': can_message,
    }
    
    return render(request, 'accounts/profile.html', context)


@login_required(login_url='login')
def edit_profile(request):
    """Edit user profile"""
    profile = request.user.profile
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user.first_name = form.cleaned_data.get('first_name', '')
            profile.user.last_name = form.cleaned_data.get('last_name', '')
            profile.user.email = form.cleaned_data.get('email', '')
            profile.user.save()
            profile.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile', username=request.user.username)
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'accounts/edit_profile.html', {'form': form})


@login_required(login_url='login')
def follow_user(request, username):
    """Follow a user"""
    user_to_follow = get_object_or_404(User, username=username)
    
    if request.user == user_to_follow:
        messages.warning(request, "You can't follow yourself!")
        return redirect('profile', username=username)
    
    follow, created = Follow.objects.get_or_create(
        follower=request.user,
        following=user_to_follow
    )
    
    if created:
        messages.success(request, f"You are now following {user_to_follow.username}!")
    else:
        messages.info(request, f"You are already following {user_to_follow.username}.")
    
    return redirect('profile', username=username)


@login_required(login_url='login')
def unfollow_user(request, username):
    """Unfollow a user"""
    user_to_unfollow = get_object_or_404(User, username=username)
    
    Follow.objects.filter(
        follower=request.user,
        following=user_to_unfollow
    ).delete()
    
    messages.success(request, f"You have unfollowed {user_to_unfollow.username}.")
    return redirect('profile', username=username)


@login_required(login_url='login')
def followers_list(request, username):
    """View user's followers"""
    user = get_object_or_404(User, username=username)
    followers = Follow.objects.filter(following=user).select_related('follower', 'follower__profile')
    
    # Check follow status for current user on each follower
    for follow in followers:
        follow.is_followed_by_current_user = Follow.objects.filter(
            follower=request.user,
            following=follow.follower
        ).exists()
    
    context = {
        'user': user,
        'followers': followers,
        'followers_count': followers.count(),
    }
    
    return render(request, 'accounts/followers_list.html', context)


@login_required(login_url='login')
def following_list(request, username):
    """View users that a user is following"""
    user = get_object_or_404(User, username=username)
    following = Follow.objects.filter(follower=user).select_related('following', 'following__profile')
    
    # Check follow status for current user on each followed user
    for follow in following:
        follow.is_followed_by_current_user = Follow.objects.filter(
            follower=request.user,
            following=follow.following
        ).exists()
    
    context = {
        'user': user,
        'following': following,
        'following_count': following.count(),
    }
    
    return render(request, 'accounts/following_list.html', context)

