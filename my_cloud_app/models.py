from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager


# Create your models here.


class User(AbstractUser):
    REQUIRED_FIELDS = ['username']
    USERNAME_FIELD = 'login'
    login = models.CharField(max_length=20, unique=True, null=True)
    username = models.CharField(max_length=50, null=True)
    password = models.CharField(max_length=100, null=True)
    email = models.EmailField(max_length=100, null=True)
    is_admin = models.BooleanField(default=False, null=True)
    path = models.TextField(null=True)

    objects = UserManager()
    def __str__(self):
        return self.login


class File(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=50, null=True)
    description = models.CharField(max_length=300, null=True)
    date_upload = models.DateField(auto_now_add=True, null=True)
    date_download = models.DateTimeField(auto_now_add=True, null=True)
    file_path = models.TextField(null=True)
    file_size = models.FloatField(null=True)

    def __str__(self):
        return self.file_name
