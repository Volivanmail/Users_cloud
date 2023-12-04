from django.urls import path
# from rest_framework import routers

from my_cloud_app.views import login_user, logout_user, register_user, list_users, delete_user, get_list_files, \
    delete_file, get_list_files_admin, upload_file

# router = routers.DefaultRouter()
urlpatterns = [
    path('login/', login_user),
    path('logout/', logout_user),
    path('register/', register_user),
    path('admin/get_users/', list_users),
    path('admin/delete_user/', delete_user),
    path('get_files/', get_list_files),
    path('delete_file/', delete_file),
    path('admin/get_user_files/', get_list_files_admin),
    path('upload_file/', upload_file)
]

