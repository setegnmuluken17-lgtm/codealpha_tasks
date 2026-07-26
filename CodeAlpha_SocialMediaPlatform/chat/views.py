from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import Follow
from .forms import DirectMessageForm
from .models import DirectMessage


def are_friends(user, other_user):
    """Friends are users who follow each other."""
    if not user.is_authenticated or user == other_user:
        return False

    return (
        Follow.objects.filter(follower=user, following=other_user).exists()
        and Follow.objects.filter(follower=other_user, following=user).exists()
    )


def friend_users(user):
    following_ids = Follow.objects.filter(follower=user).values_list('following_id', flat=True)
    follower_ids = Follow.objects.filter(following=user).values_list('follower_id', flat=True)
    mutual_ids = set(following_ids).intersection(set(follower_ids))
    return User.objects.filter(id__in=mutual_ids).select_related('profile').order_by('username')


@login_required(login_url='login')
def inbox(request):
    """Show friends and the latest message with each friend."""
    conversations = []
    for friend in friend_users(request.user):
        messages_qs = DirectMessage.objects.filter(
            Q(sender=request.user, recipient=friend) | Q(sender=friend, recipient=request.user)
        )
        conversations.append({
            'friend': friend,
            'last_message': messages_qs.order_by('-created_at').first(),
            'unread_count': messages_qs.filter(recipient=request.user, is_read=False).count(),
        })

    conversations.sort(
        key=lambda item: item['last_message'].created_at if item['last_message'] else item['friend'].date_joined,
        reverse=True,
    )

    return render(request, 'chat/inbox.html', {'conversations': conversations})


@login_required(login_url='login')
def thread(request, username):
    """View and send messages with one friend."""
    friend = get_object_or_404(User.objects.select_related('profile'), username=username)

    if not are_friends(request.user, friend):
        messages.error(request, 'You can only message friends who follow you back.')
        return redirect('profile', username=friend.username)

    if request.method == 'POST':
        form = DirectMessageForm(request.POST, request.FILES)
        if form.is_valid():
            direct_message = form.save(commit=False)
            direct_message.sender = request.user
            direct_message.recipient = friend
            direct_message.save()
            return redirect('chat_thread', username=friend.username)
    else:
        form = DirectMessageForm()

    thread_messages = DirectMessage.objects.filter(
        Q(sender=request.user, recipient=friend) | Q(sender=friend, recipient=request.user)
    ).select_related('sender', 'recipient').order_by('created_at')

    thread_messages.filter(recipient=request.user, is_read=False).update(is_read=True)

    return render(request, 'chat/thread.html', {
        'friend': friend,
        'form': form,
        'thread_messages': thread_messages,
    })
