# Generated by Django 3.2.12 on 2022-09-14 23:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('alpha', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='land',
            name='author',
        ),
    ]
