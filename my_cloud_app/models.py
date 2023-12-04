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
    file_name = models.CharField(max_length=50)
    description = models.CharField(max_length=300)
    date_upload = models.DateField(auto_now_add=True)
    date_download = models.DateTimeField(auto_now_add=True)
    file_path = models.TextField()
    file_size = models.FloatField()

    def __str__(self):
        return self.file_name
