import os

from django import forms
from django.conf import settings

from .models import DirectMessage


class DirectMessageForm(forms.ModelForm):
    """Compose a text message, a voice message, or both."""

    class Meta:
        model = DirectMessage
        fields = ('text', 'voice')
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write a message...',
                'rows': 2,
                'style': 'resize: none;',
            }),
            'voice': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'audio/*',
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        text = cleaned_data.get('text', '').strip()
        voice = cleaned_data.get('voice')

        if not text and not voice:
            raise forms.ValidationError('Write a message or attach a voice message.')

        cleaned_data['text'] = text
        return cleaned_data

    def clean_voice(self):
        voice = self.cleaned_data.get('voice')
        if not voice:
            return voice

        content_type = getattr(voice, 'content_type', None)
        size = getattr(voice, 'size', None)
        name = getattr(voice, 'name', '')
        ext = os.path.splitext(name)[1].lower()

        allowed_types = getattr(settings, 'VOICE_ALLOWED_CONTENT_TYPES', [])
        allowed_exts = getattr(settings, 'VOICE_ALLOWED_EXTENSIONS', [])
        max_size = getattr(settings, 'VOICE_MAX_UPLOAD_SIZE', 15 * 1024 * 1024)

        if content_type and content_type not in allowed_types:
            raise forms.ValidationError('Unsupported voice format. Allowed: mp3, wav, webm, ogg, m4a.')
        if ext and ext not in allowed_exts:
            raise forms.ValidationError('Unsupported voice file extension. Allowed: .mp3, .wav, .webm, .ogg, .m4a.')
        if size and size > max_size:
            max_mb = max_size // (1024 * 1024)
            raise forms.ValidationError(f'Voice message is too large. Maximum size is {max_mb} MB.')

        return voice
