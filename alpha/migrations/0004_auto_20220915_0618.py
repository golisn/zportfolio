# Generated by Django 3.2.12 on 2022-09-15 06:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('alpha', '0003_auto_20220914_2348'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='land',
            name='create_at',
        ),
        migrations.RemoveField(
            model_name='land',
            name='file_upload',
        ),
        migrations.RemoveField(
            model_name='land',
            name='head_image',
        ),
        migrations.RemoveField(
            model_name='land',
            name='hook_text',
        ),
        migrations.RemoveField(
            model_name='land',
            name='title',
        ),
        migrations.RemoveField(
            model_name='land',
            name='update_at',
        ),
        migrations.AlterField(
            model_name='land',
            name='author',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
