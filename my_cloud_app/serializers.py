from rest_framework import serializers
from .models import User, File


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['login', 'username', 'password', 'email']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(login=validated_data['login'], username=validated_data['username'], email=validated_data['email'])
        user.set_password(validated_data['password'])
        user.save()

        return user


class FullUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class ListUsersSerializer(serializers.ModelSerializer):
    file_count = serializers.IntegerField()
    total_count = serializers.IntegerField()

    class Meta:
        model = User
        fields = ['id', 'login', 'username', 'email', 'is_admin', 'file_count', 'total_count']


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = "__all__"
        # fields = ['user', 'file_name', 'description']



