from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0003_story'),
    ]

    operations = [
        migrations.CreateModel(
            name='StoryLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('story', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='posts.story')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='liked_stories', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'unique_together': {('story', 'user')},
                'indexes': [
                    models.Index(fields=['story', '-created_at'], name='posts_story_story_i_0e85f8_idx'),
                    models.Index(fields=['user', '-created_at'], name='posts_story_user_id_1afe3d_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='StoryView',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('viewed_at', models.DateTimeField(auto_now_add=True)),
                ('story', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='views', to='posts.story')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='story_views', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-viewed_at'],
                'unique_together': {('story', 'user')},
                'indexes': [
                    models.Index(fields=['story', '-viewed_at'], name='posts_story_story_i_f8f3df_idx'),
                    models.Index(fields=['user', '-viewed_at'], name='posts_story_user_id_1ac73d_idx'),
                ],
            },
        ),
    ]
