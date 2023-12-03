from django.urls import path
# from rest_framework import routers

from my_cloud_app.views import login_user, logout_user, register_user

# router = routers.DefaultRouter()
urlpatterns = [
    path('login/', login_user),
    path('logout/', logout_user),
    path('register/', register_user)
]

