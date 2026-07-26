import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import posts.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0002_post_video'),
    ]

    operations = [
        migrations.CreateModel(
            name='Story',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('caption', models.CharField(blank=True, max_length=300)),
                ('image', models.ImageField(blank=True, null=True, upload_to='story_images/')),
                ('video', models.FileField(blank=True, null=True, upload_to='story_videos/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField(default=posts.models.story_expiry_time)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stories', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['author', '-created_at'], name='posts_story_author__e3d456_idx'),
                    models.Index(fields=['expires_at', '-created_at'], name='posts_story_expires_73f2c2_idx'),
                ],
            },
        ),
    ]
