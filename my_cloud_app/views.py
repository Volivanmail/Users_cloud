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
from .config import BASE_DIR_STORAGE, LENGTH_OF_THE_DOWNLOAD_LINK
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
            user = authenticate(serializer.initial_data['login'], serializer.initial_data['password'])
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
                                   'Выход пользователя осушествлен успешно',
                                   True)
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
        try:
            user = User.objects.get(pk=request.user.id)
            request_file = request.FILES['file']
            fs = FileSystemStorage(location=f'{BASE_DIR_STORAGE}{user.path}', base_url=user.path)
            file = fs.save(request_file.name, request_file)
            print(file)
            file_url = fs.url(file)
            print(file_url)
            file_size = fs.size(file)
            parts_url = file_url.split('/')
            file_name = parts_url[-1]
            print(file_name)
            new_file = File.objects.create(user=user,
                                           file_name=file_name,
                                           description=request.data['description'],
                                           file_path=file_url,
                                           file_size=file_size
                                           )
            new_file.save()
            message = create_message_for_upload_file(request_file.name, file_name)
            print(message)
            return create_response(status.HTTP_200_OK,
                                   message,
                                   True,
                                   {'file': request_file.name})
        except Exception as e:
            return create_response(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))


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


# не проходит
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_file(request):
    try:
        if request.method == 'GET':
            print(request.data)
            file_id = request.GET.get('file_id')
            file = File.objects.get(pk=file_id)
            print(file)
            file_path = f'{BASE_DIR_STORAGE}{file.file_path}'
            filename = file.file_name
            return create_file_response(file_path, filename)
    except Exception as e:
        return create_response(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))


# получается
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def creating_link_to_the_file(request):
    try:
        if request.method == 'GET':
            user_id = request.GET.get('user_id')
            file_id = request.GET.get('file_id')
            characters = string.ascii_letters + string.digits
            one_time_link = ''.join(random.choices(characters, k=int(LENGTH_OF_THE_DOWNLOAD_LINK)))
            File.objects.filter(pk=file_id, user=user_id).update(link_for_download=one_time_link)
            return create_response(status.HTTP_200_OK,
                                   'Создана ссылка на скачивание',
                                   True,
                                   {'link': one_time_link})
    except Exception as e:
        return create_response(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))


# не проходит
@api_view(['GET'])
def download_file_from_link(request):
    try:
        if request.method == 'GET':
            one_time_link = request.GET.get['link']
            file = File.objects.filter(link_for_download=one_time_link)
            file_path = file.file_path
            filename = file.file_name
            response = create_file_response(file_path, filename)
            file.link_for_download = ''
            file.save(update_fields=['link_for_download'])
            return response
    except Exception as e:
        return create_response(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))
