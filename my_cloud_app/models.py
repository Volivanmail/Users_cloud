from django.db import models


# Create your models here.

class User(models.Model):
    # REQUIRED_FIELDS = ('user',)
    login = models.CharField(max_length=20, unique=True, null=True)
    username = models.CharField(max_length=50)
    email = models.EmailField(max_length=100)
    is_admin = models.BooleanField(default=False)
    path = models.TextField()


class File(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=50)
    description = models.CharField(max_length=300)
    date_upload = models.DateField(auto_now_add=True)
    date_download = models.DateTimeField(auto_now_add=True)
    file_path = models.TextField()
    file_size = models.FloatField()

