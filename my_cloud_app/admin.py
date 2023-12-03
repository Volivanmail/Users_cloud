from django.contrib import admin
from .models import User, File


class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "login", "name", "surname", "email", "password", "admin")
    list_display_links = ("id", "login")
    search_fields = ("id", "login", "name", "surname")
    list_filter = ("id", "login", "name", "surname")


admin.site.register(User)


class FileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "file_name", "description", "date_upload", "date_download", "file_path", "file_size")
    list_display_links = ("user", "file_name")
    search_fields = ("user", "file_name", "date_upload", "date_download", "file_size")
    list_filter = ("user", "file_name", "date_upload", "date_download", "file_size")


admin.site.register(File)

