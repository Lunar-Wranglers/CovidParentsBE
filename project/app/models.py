from django.contrib.auth import get_user_model
from django.db import models
from django.conf import settings

# Create your models here.

class Link(models.Model):
    url = models.URLField()
    description = models.TextField(blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)

class Image(models.Model):
    """Image"""
    image = models.ImageField(upload_to="images/")
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)

    def __str__(self):
        """Return image"""
        return self.image.url

class Post(models.Model):
    """Post"""
    title = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="post-images/")
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)

    def __str__(self):
        """Return image"""
        return self.image.url