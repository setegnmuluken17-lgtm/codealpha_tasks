from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.files.storage import default_storage
from datetime import timedelta


def story_expiry_time():
    return timezone.now() + timedelta(hours=24)


class Post(models.Model):
    """Model for user posts"""
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    video = models.FileField(upload_to='post_videos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"Post by {self.author.username} on {self.created_at}"

    def save(self, *args, **kwargs):
        """Remove old media files when an image or video is replaced."""
        if self.pk:
            try:
                old_post = Post.objects.get(pk=self.pk)
            except Post.DoesNotExist:
                old_post = None

            if old_post:
                if old_post.image and old_post.image != self.image:
                    default_storage.delete(old_post.image.name)
                if old_post.video and old_post.video != self.video:
                    default_storage.delete(old_post.video.name)

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Delete uploaded media files when the post is deleted."""
        image_name = self.image.name if self.image else None
        video_name = self.video.name if self.video else None

        super().delete(*args, **kwargs)

        if image_name:
            default_storage.delete(image_name)
        if video_name:
            default_storage.delete(video_name)
    
    def like_count(self):
        """Get total likes for this post"""
        return self.likes.count()
    
    def comment_count(self):
        """Get total comments for this post"""
        return self.comments.count()


class Like(models.Model):
    """Model for post likes"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liked_posts')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('post', 'user')
        indexes = [
            models.Index(fields=['post', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} liked {self.post.author.username}'s post"


class Comment(models.Model):
    """Model for post comments"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['post', '-created_at']),
            models.Index(fields=['author', '-created_at']),
        ]
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.author.username}'s post"


class Story(models.Model):
    """Short-lived user story that expires after 24 hours."""
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stories')
    caption = models.CharField(max_length=300, blank=True)
    image = models.ImageField(upload_to='story_images/', blank=True, null=True)
    video = models.FileField(upload_to='story_videos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=story_expiry_time)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['expires_at', '-created_at']),
        ]

    def __str__(self):
        return f"Story by {self.author.username}"

    @property
    def is_active(self):
        return self.expires_at > timezone.now()

    def delete(self, *args, **kwargs):
        image_name = self.image.name if self.image else None
        video_name = self.video.name if self.video else None

        super().delete(*args, **kwargs)

        if image_name:
            default_storage.delete(image_name)
        if video_name:
            default_storage.delete(video_name)

    def view_count(self):
        return self.views.count()

    def like_count(self):
        return self.likes.count()


class StoryView(models.Model):
    """Tracks which users viewed a story."""
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='story_views')
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('story', 'user')
        ordering = ['-viewed_at']
        indexes = [
            models.Index(fields=['story', '-viewed_at']),
            models.Index(fields=['user', '-viewed_at']),
        ]

    def __str__(self):
        return f"{self.user.username} viewed {self.story.author.username}'s story"


class StoryLike(models.Model):
    """Tracks story likes."""
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liked_stories')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('story', 'user')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['story', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} liked {self.story.author.username}'s story"
