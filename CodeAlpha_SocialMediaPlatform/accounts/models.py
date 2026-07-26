from django.db import models
from django.contrib.auth.models import User
from django.core.validators import URLValidator
from django.utils import timezone


class UserProfile(models.Model):
    """Extended user profile model with social features"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True, max_length=500)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    profile_picture_thumbnail = models.ImageField(upload_to='profile_pictures/thumbs/', blank=True, null=True)
    cover_photo = models.ImageField(upload_to='cover_photos/', blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    joined_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    class Meta:
        ordering = ['-joined_date']

    def save(self, *args, **kwargs):
        """Generate a thumbnail for profile_picture on save."""
        super().save(*args, **kwargs)  # save original first to ensure file exists

        if self.profile_picture:
            try:
                from PIL import Image
                import io
                from django.core.files.base import ContentFile

                img = Image.open(self.profile_picture.path)
                img.convert('RGB')
                img.thumbnail((300, 300))

                thumb_io = io.BytesIO()
                img.save(thumb_io, format='JPEG', quality=85)
                thumb_name = f"thumb_{self.profile_picture.name.split('/')[-1]}"

                # Save thumbnail to field
                self.profile_picture_thumbnail.save(thumb_name, ContentFile(thumb_io.getvalue()), save=False)
                super().save(update_fields=['profile_picture_thumbnail'])
            except Exception:
                # If thumbnail generation fails, ignore and proceed
                pass


class Follow(models.Model):
    """Model to track user follows"""
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('follower', 'following')
        indexes = [
            models.Index(fields=['follower', 'created_at']),
            models.Index(fields=['following', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"
