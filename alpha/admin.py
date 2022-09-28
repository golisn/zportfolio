from django.contrib import admin

# Register your models here.
from .models import Post_info, Post_qa, land, Post
admin.site.register(Post)
admin.site.register(Post_qa)
admin.site.register(Post_info)
admin.site.register(land)