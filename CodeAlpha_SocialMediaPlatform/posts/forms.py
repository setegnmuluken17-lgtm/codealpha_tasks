from django import forms
from .models import Post, Comment, Story


class PostForm(forms.ModelForm):
    """Form for creating and editing posts"""
    remove_video = forms.BooleanField(
        required=False,
        label='Remove current video',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = Post
        fields = ('content', 'image', 'video')
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': "What's on your mind?",
                'rows': 4,
                'style': 'resize: none;'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'video': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'video/*'
            }),
        }
    
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if not content:
            raise forms.ValidationError("Post content cannot be empty.")
        if len(content) > 5000:
            raise forms.ValidationError("Post content cannot exceed 5000 characters.")
        return content

    def clean_video(self):
        """Server-side validation for uploaded videos: type, extension, and size."""
        video = self.cleaned_data.get('video')
        if not video:
            return video

        import os
        from django.conf import settings

        content_type = getattr(video, 'content_type', None)
        size = getattr(video, 'size', None)
        name = getattr(video, 'name', '')
        ext = os.path.splitext(name)[1].lower()

        allowed_types = getattr(settings, 'VIDEO_ALLOWED_CONTENT_TYPES', ['video/mp4', 'video/webm', 'video/quicktime'])
        allowed_exts = getattr(settings, 'VIDEO_ALLOWED_EXTENSIONS', ['.mp4', '.webm', '.mov'])
        max_size = getattr(settings, 'VIDEO_MAX_UPLOAD_SIZE', 50 * 1024 * 1024)

        # Validate content type
        if content_type and content_type not in allowed_types:
            raise forms.ValidationError("Unsupported video format. Allowed types: mp4, webm, mov.")

        # Validate extension
        if ext and ext not in allowed_exts:
            raise forms.ValidationError("Unsupported video file extension. Allowed extensions: .mp4, .webm, .mov")

        # Validate size
        if size and size > max_size:
            max_mb = max_size // (1024 * 1024)
            raise forms.ValidationError(f"Video file is too large. Maximum size is {max_mb} MB.")

        return video


class CommentForm(forms.ModelForm):
    """Form for creating comments on posts"""
    
    class Meta:
        model = Comment
        fields = ('content',)
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write a comment...',
                'rows': 2,
                'style': 'resize: none;'
            }),
        }
    
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if not content:
            raise forms.ValidationError("Comment cannot be empty.")
        if len(content) > 1000:
            raise forms.ValidationError("Comment cannot exceed 1000 characters.")
        return content


class StoryForm(forms.ModelForm):
    """Form for creating 24-hour stories."""

    class Meta:
        model = Story
        fields = ('caption', 'image', 'video')
        widgets = {
            'caption': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Add a short caption...',
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'video': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'video/*'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get('image')
        video = cleaned_data.get('video')
        caption = cleaned_data.get('caption')

        if not image and not video and not caption:
            raise forms.ValidationError("Add a caption, image, or video to create a story.")

        return cleaned_data

    def clean_video(self):
        video = self.cleaned_data.get('video')
        if not video:
            return video

        import os
        from django.conf import settings

        content_type = getattr(video, 'content_type', None)
        size = getattr(video, 'size', None)
        name = getattr(video, 'name', '')
        ext = os.path.splitext(name)[1].lower()

        allowed_types = getattr(settings, 'VIDEO_ALLOWED_CONTENT_TYPES', ['video/mp4', 'video/webm', 'video/quicktime'])
        allowed_exts = getattr(settings, 'VIDEO_ALLOWED_EXTENSIONS', ['.mp4', '.webm', '.mov'])
        max_size = getattr(settings, 'VIDEO_MAX_UPLOAD_SIZE', 50 * 1024 * 1024)

        if content_type and content_type not in allowed_types:
            raise forms.ValidationError("Unsupported video format. Allowed types: mp4, webm, mov.")
        if ext and ext not in allowed_exts:
            raise forms.ValidationError("Unsupported video file extension. Allowed extensions: .mp4, .webm, .mov")
        if size and size > max_size:
            max_mb = max_size // (1024 * 1024)
            raise forms.ValidationError(f"Video file is too large. Maximum size is {max_mb} MB.")

        return video
