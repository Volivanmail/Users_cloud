from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FileUploadParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import User, File
from .permissions import IsAdmin
from .serializers import UserSerializer, FullUserSerializer, FileSerializer




# Create your views here.

# блок api для работы с пользователями
def create_response(status_code, message, success=False, data=None):
    response = {
        "status": status_code,
        "message": message,
        "success": success
    }

    if data:
        response["data"] = data
    return Response(status=status_code, data=response)


@api_view(['POST'])
def register_user(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return create_response(status.HTTP_201_CREATED,
                                   'Пользователь успешно зарегистрирован',
                                   True,
                                   serializer.data)
        return create_response(status.HTTP_400_BAD_REQUEST,
                               'Ошибка регистрации пользователя')


@api_view(['POST'])
def login_user(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        user = None
        try:
            user = User.objects.get(login=serializer.initial_data['login'])
        except ObjectDoesNotExist:
            pass
        if not user:
            user = authenticate(serializer.login, serializer.password)
        if user:
            token = Token.objects.create(user=user)
            return create_response(status.HTTP_200_OK,
                                   'Авторизация прошла успешно',
                                   True,
                                   {'token': token.key})
        return create_response(status.HTTP_401_UNAUTHORIZED,
                               'Ошибка авторизации')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    if request.method == 'POST':
        try:
            request.user.auth_token.delete()
            return create_response(status.HTTP_200_OK,
                                            'Выход пользователя осушествлен успешно', True)
        except Exception as e:
            return Response(create_response(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e)))


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def list_users(request):
    if request.method == 'GET':
        try:
            users = User.objects.values_list('login', 'username', 'email', 'is_admin')
            # print(users)
            serializer_users = FullUserSerializer(users, many=True)
            serializer_users.is_valid()
            result = serializer_users.data
            return create_response(status.HTTP_200_OK,
                                   'Получен список пользователей',
                                   True,
                                   {'users': result})
        except Exception as e:
            return create_response(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))


@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdmin])
def edit_user(request):
    if request.method == 'PUT':
        try:
            serializer = FullUserSerializer(data=request.data)
            User.objects.filter(pk=serializer.initial_data['id']).update(is_admin=serializer.initial_data['is_admin'])
            user = User.objects.get(pk=serializer.initial_data['id'])
            return create_response(status.HTTP_200_OK,
                                   'Изменение статуса пользователя прошло успешно',
                                   True,
                                   {'login': user.login, 'is_admin': user.is_admin})
        except Exception as e:
            return create_response(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdmin])
def delete_user(request):
    if request.method == 'DELETE':
        try:
            serializer = FullUserSerializer(data=request.data)
            user = User.objects.get(pk=serializer.initial_data['id'])
            user.delete()
            return create_response(status.HTTP_200_OK,
                                   'Пользователь удален',
                                   True,)
        except Exception as e:
            return create_response(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))


# блок api для работы с файловым хранилищем

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_list_files(request):
    if request.method == 'GET':
        try:
            serializer = FullUserSerializer(data=request.data)
            user = User.objects.get(pk=serializer.initial_data['id'])
            files = File.objects.filter(user=user).values_list()
            return create_response(status.HTTP_200_OK,
                                   'Получен список файлов пользователя',
                                   True,
                                   {'files': files})
        except Exception as e:
            return create_response(status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   str(e))


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def get_list_files_admin(request):
    if request.method == 'GET':
        try:
            user_id = request.GET.get("user_id")
            user = User.objects.get(pk=user_id)
            files = File.objects.filter(user=user).values_list()
            return create_response(status.HTTP_200_OK,
                                   'Получен список файлов пользователя',
                                   True,
                                   {'files': files})
        except Exception as e:
            return create_response(status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   str(e))

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FileUploadParser])
def upload_file(request):
    if request.method == 'POST':
        file = request.FILES['file']
        print(FileSystemStorage(location='/my_cloud_app/storage').save(file.name, file))
        return Response()



@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_file(request):
    if request.method == 'DELETE':
        try:
            serializer = FileSerializer(data=request.data)
            file = File.objects.get(pk=serializer.initial_data['id'])
            file.delete()
            return create_response(status.HTTP_200_OK,
                                   'Файл удален',
                                   True, )
        except Exception as e:
            return create_response(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))


# @api_view(['PUT'])
# @permission_classes([IsAuthenticated])
# def rename_file(request):
#     if request.method == 'PUT':
#
#
# @api_view(['PUT'])
# @permission_classes([IsAuthenticated])
# def edit_description_file(request):
#     if request.method == 'PUT':
#
#
# @api_view([''])
# @permission_classes([IsAuthenticated])
# def download_file(request):
#     if request.method == '':
#
#
# @api_view([''])
# @permission_classes([IsAuthenticated])
# def creating_link_to_the_file(request):
#     if request.method == '':
#
#
# @api_view([''])
# @permission_classes([IsAuthenticated])
# def download_file_from_link(request):
#     if request.method == '':
