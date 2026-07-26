from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.db import models


class DirectMessage(models.Model):
    """Private text or voice message between two friends."""
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    text = models.TextField(blank=True)
    voice = models.FileField(upload_to='voice_messages/', blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['sender', 'recipient', 'created_at']),
            models.Index(fields=['recipient', 'is_read', 'created_at']),
        ]

    def __str__(self):
        return f"Message from {self.sender.username} to {self.recipient.username}"

    @property
    def has_voice(self):
        return bool(self.voice)

    def delete(self, *args, **kwargs):
        voice_name = self.voice.name if self.voice else None
        super().delete(*args, **kwargs)
        if voice_name:
            default_storage.delete(voice_name)
