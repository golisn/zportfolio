# Generated by Django 3.2.12 on 2022-08-31 06:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='land',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=20)),
                ('hook_text', models.CharField(blank=True, max_length=100)),
                ('content', models.TextField()),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('update_at', models.DateTimeField(auto_now=True)),
                ('head_image', models.ImageField(blank=True, upload_to='blog/imges/%Y/%m/%d/')),
                ('file_upload', models.FileField(blank=True, upload_to='blog/files/%Y/%m/%d/')),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
