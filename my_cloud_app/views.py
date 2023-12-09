import random
import string

from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import FileSystemStorage
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FileUploadParser
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import User, File
from .permissions import IsAdmin
from .serializers import UserSerializer, FullUserSerializer, FileSerializer
from .config import BASE_DIR_STORAGE
from .utils import *


# Create your views here.

# блок api для работы с пользователями


@api_view(['POST'])
def register_user(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user = User.objects.get(login=serializer.initial_data['login'])
            user.path = f'/{user.id}'
            user.save(update_fields=['path'])
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
            users = User.objects.all().values('login', 'username', 'email', 'is_admin')
            serializer_users = FullUserSerializer(users, many=True)
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
            user_id = request.GET.get("id")
            user = User.objects.get(pk=user_id)
            files = File.objects.filter(user=user).values()
            return create_response(status.HTTP_200_OK,
                                   'Получен список файлов пользователя',
                                   True,
                                   {'files': files})
        except Exception as e:
            return create_response(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def get_list_files_admin(request):
    if request.method == 'GET':
        try:
            user_id = request.GET.get("user_id")
            user = User.objects.get(pk=user_id)
            files = File.objects.filter(user=user).values()
            return create_response(status.HTTP_200_OK,
                                   'Получен список файлов пользователя',
                                   True,
                                   {'files': files})
        except Exception as e:
            return create_response(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FileUploadParser])
def upload_file(request):
    if request.method == 'POST':
        # Дописать сохранение пути файла в базу
        # Дописать сохранение в папку пользователя
        # Вернуть нормальный респонс
        # Размер файла
        # поменял fs = .....
        try:
            user_id = request.user.id
            user = User.objects.get(pk=request.user.id)
            request_file = request.FILES['file']
            fs = FileSystemStorage(location=f'{BASE_DIR_STORAGE}{user.path}', base_url=user.path)
            file = fs.save(request_file.name, request_file)
            file_url = fs.url(file)
            file_size = fs.size(file)
            new_file = File.objects.create(file_name=request_file.name,
                                           description=request.FILES['description'],
                                           file_path=file_url,
                                           file_size=file_size
                                           )
            new_file.save()
            return create_response(status.HTTP_200_OK,
                                   f'Файл {request_file.name} загружен как файл {new_file.name}',
                                   True,
                                   {'file': request_file.name})
        except Exception as e:
            return create_response(status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   str(e))


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


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def rename_file(request):
    if request.method == 'PUT':
        try:
            previous_file_name = File.objects.filter(pk=request.data['id']).values('file_name')
            serializer = FileSerializer(data=request.data)
            new_file_name = serializer.initial_data['file_name']
            File.objects.filter(pk=serializer.initial_data['id']).update(file_name=new_file_name)
            return create_response(status.HTTP_200_OK,
                                   'Имя файла изменено!',
                                   True,
                                   {'previous file name': previous_file_name,
                                    'new_file_name ': new_file_name})
        except Exception as e:
            return create_response(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_description_file(request):
    if request.method == 'PUT':
        try:
            serializer = FileSerializer(data=request.data)
            File.objects.filter(pk=serializer.initial_data['id']).update(file_name=serializer.initial_data['description'])
            file = File.objects.get(pk=serializer.initial_data['id'])
            return create_response(status.HTTP_200_OK,
                                   'Обновление описания файла',
                                   True,
                                   {'file_name': file.file_name,
                                    'new_description': file.description})
        except Exception as e:
            return create_response(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_file(request):
    if request.method == 'GET':
        # заменить данные файла
        file_path = 'text.txt'
        filename = 'text.txt'

        return create_file_response(file_path, filename)
#
#
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def creating_link_to_the_file(request):
    if request.method == 'GET':
        length = 20
        characters = string.ascii_letters + string.digits
        one_time_link = ''.join(random.choices(characters, k=length))
        # созранить в базу ссылку для файла
        # вернул респонс


@api_view(['GET'])
def download_file_from_link(request):
    if request.method == 'GET':
        one_time_link = request.GET.get['link']
        # пошел в базу, нашел файл по ссылку
        file_path = ''
        filename = ''
        response = create_file_response(file_path, filename)
        # удалил ссылку
        return response
