from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class land(models.Model):
    title = models.CharField(max_length=20)
    hook_text = models.CharField(max_length=100, blank=True)
    content = models.TextField()

    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    head_image = models.ImageField(upload_to='blog/imges/%Y/%m/%d/', blank = True)
    file_upload = models.FileField(upload_to='blog/files/%Y/%m/%d/', blank = True)

    # author = models.ForeignKey(User, on_delete=models.CASCADE) 작성자를 지우면 포스트 지우는 코딩
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)  # 작성자를 지워도 포스트는 남는 코딩