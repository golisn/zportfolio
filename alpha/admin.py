from django.contrib import admin

# Register your models here.
from .models import land, Post
admin.site.register(Post)