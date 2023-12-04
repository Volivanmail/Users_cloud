from django.db import models
from django.contrib.auth.models import AbstractBaseUser

# Create your models here.


class User(AbstractBaseUser):
    REQUIRED_FIELDS = ['username']
    USERNAME_FIELD = 'login'
    login = models.CharField(max_length=20, unique=True, null=True)
    username = models.CharField(max_length=50, null=True)
    password = models.CharField(max_length=100, null=True)
    email = models.EmailField(max_length=100, null=True)
    is_admin = models.BooleanField(default=False, null=True)
    path = models.TextField(null=True)


class File(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=50, null=True)
    description = models.CharField(max_length=300, null=True)
    date_upload = models.DateField(auto_now_add=True, null=True)
    date_download = models.DateTimeField(auto_now_add=True, null=True)
    file_path = models.TextField(null=True)
    file_size = models.FloatField(null=True)

