import os
import random
import string
import logging
import datetime

from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import FileSystemStorage
from django.db.models import Count, Sum

from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FileUploadParser
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import User, File
from .permissions import IsAdmin
from .serializers import UserSerializer, FullUserSerializer, FileSerializer, ListUsersSerializer
from .config import BASE_DIR_STORAGE, LENGTH_OF_THE_DOWNLOAD_LINK
from .utils import *

logger = logging.getLogger('my_cloud_api')

# блок api для работы с пользователями


@api_view(['POST'])
def register_user(request):
    try:
        if request.method == 'POST':
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                user = User.objects.get(login=serializer.initial_data['login'])
                user.path = f'/{user.id}'
                user.save(update_fields=['path'])
                logger.info("Пользователь зарегистрирован")
                return create_response(status.HTTP_201_CREATED,
                                       'Пользователь успешно зарегистрирован',
                                       True,
                                       serializer.data)
            logger.error("Ошибка регистрации пользователя")
            return create_response(status.HTTP_400_BAD_REQUEST,
                                   'Ошибка регистрации пользователя')
    except Exception as e:
        logger.error(str(e))
        return Response(create_response(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e)))


@api_view(['POST'])
def login_user(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        user = None
        try:
            user = User.objects.get(login=serializer.initial_data['login'])
            user.auth_token.delete()
        except ObjectDoesNotExist:
            pass
        if user is not None:
            user = authenticate(username=serializer.initial_data['login'], password=serializer.initial_data['password'])
        if user:
            token = Token.objects.create(user=user)
            logger.info("Авторизация прошла успешно")
            return create_response(status.HTTP_200_OK,
                                   'Авторизация прошла успешно',
                                   True,
                                   {'id': user.id,
                                    'login': user.login,
                                    'token': token.key,
                                    'is_admin': user.is_admin})
        logger.error("Ошибка авторизации")
        return create_response(status.HTTP_401_UNAUTHORIZED,
                               'Ошибка авторизации')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    if request.method == 'POST':
        try:
            request.user.auth_token.delete()
            logger.info("Выход пользователя осушествлен успешно")
            return create_response(status.HTTP_200_OK,
                                   'Выход пользователя осушествлен успешно',
                                   True)
        except Exception as e:
            logger.error(str(e))
            return Response(create_response(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e)))


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def list_users(request):
    if request.method == 'GET':
        try:
            users_with_file_count = User.objects.annotate(file_count=Count('file'),
                                                          total_count=Sum('file__file_size'))

            serializer_users = ListUsersSerializer(users_with_file_count, many=True)
            result = serializer_users.data

            logger.info('Получен список пользователей')
            return create_response(status.HTTP_200_OK,
                                   'Получен список пользователей',
                                   True,
                                   {'users': result}
                                   )
        except Exception as e:
            logger.error(str(e))
            return create_response(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))


@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdmin])
def edit_user(request):
    if request.method == 'PUT':
        try:
            serializer = FullUserSerializer(data=request.data)
            user = User.objects.get(pk=serializer.initial_data['id'])
            is_admin = user.is_admin
            user.is_admin = not is_admin
            user.save()
            logger.info('Изменение статуса поля is_admin пользователя прошло успешно')
            return create_response(status.HTTP_200_OK,
                                   'Изменение статуса пользователя прошло успешно',
                                   True,
                                   {'login': user.login, 'is_admin': is_admin})
        except Exception as e:
            logger.error(str(e))
            return create_response(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdmin])
def delete_user(request):
    if request.method == 'DELETE':
        try:
            user_id = request.GET.get('id')
            user = User.objects.get(pk=user_id)
            user.delete()
            logger.info("Пользователь удален")
            return create_response(status.HTTP_200_OK,
                                   'Пользователь удален',
                                   True,)
        except Exception as e:
            logger.error(str(e))
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
            logger.info("Получен список файлов пользователя")
            return create_response(status.HTTP_200_OK,
                                   'Получен список файлов пользователя',
                                   True,
                                   {'files': files})
        except Exception as e:
            logger.error(str(e))
            return create_response(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))


# работает
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def get_list_files_admin(request):
    if request.method == 'GET':
        try:
            user_id = request.GET.get("user_id")
            user = User.objects.get(pk=user_id)
            files = File.objects.filter(user=user).values()
            logger.info("Получен список файлов пользователя")
            return create_response(status.HTTP_200_OK,
                                   'Получен список файлов пользователя',
                                   True,
                                   {'files': files})
        except Exception as e:
            logger.error(str(e))
            return create_response(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))


# размер файла норм сделать, что то с кодировкой
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FileUploadParser])
def upload_file(request):
    print(request)
    if request.method == 'POST':
        try:
            user = User.objects.get(pk=request.user.id)
            request_file = request.FILES['file']
            location = f'{BASE_DIR_STORAGE}{user.path}'
            fs = FileSystemStorage(location=location)
            file = fs.save(request_file.name, request_file)
            file_path = user.path + '/' + file
            file_size = round(fs.size(file) / 1024)
            new_file = File.objects.create(user=user,
                                           file_name=file,
                                           description=request.data['description'],
                                           file_path=file_path,
                                           file_size=file_size
                                           )
            new_file.save()
            logger.info("Файл загружен")
            return create_response(status.HTTP_200_OK,
                                   f'Файл загружен как файл {file}',
                                   True,
                                   {'file': file})
        except Exception as e:
            logger.error(str(e))
            return create_response(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))


# работает
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_file(request):
    if request.method == 'DELETE':
        try:
            file_id = request.GET.get('id')
            file = File.objects.get(pk=file_id)
            os.remove(f'{BASE_DIR_STORAGE}{file.file_path}')
            file.delete()
            logger.info("Файл удален")
            return create_response(status.HTTP_200_OK,
                                   'Файл удален',
                                   True, )
        except Exception as e:
            logger.error(str(e))
            return create_response(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def rename_file(request):
    if request.method == 'PUT':
        try:
            file = File.objects.filter(pk=request.data['id'])
            serializer = FileSerializer(data=request.data)
            new_file_name = serializer.initial_data['file_name']
            File.objects.filter(pk=serializer.initial_data['id']).update(file_name=new_file_name)
            logger.info("Имя файла изменено!")
            return create_response(status.HTTP_200_OK,
                                   'Имя файла изменено!',
                                   True,
                                   {'new_file_name ': new_file_name})
        except Exception as e:
            logger.error(str(e))
            return create_response(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))


# работает
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_description_file(request):
    if request.method == 'PUT':
        try:
            serializer = FileSerializer(data=request.data)
            File.objects.filter(pk=serializer.initial_data['id'])\
                .update(description=serializer.initial_data['description'])
            file = File.objects.get(pk=serializer.initial_data['id'])
            logger.info("Обновление описания файла")
            return create_response(status.HTTP_200_OK,
                                   'Обновление описания файла',
                                   True,
                                   {'file_name': file.file_name,
                                    'new_description': file.description})
        except Exception as e:
            logger.error(str(e))
            return create_response(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))


# работает
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_file(request):
    try:
        if request.method == 'GET':
            file_id = request.GET.get('file_id')
            file = File.objects.get(pk=file_id)
            file_path = f'{BASE_DIR_STORAGE}{file.file_path}'
            filename = file.file_name
            file.date_download = datetime.datetime.now().date()
            file.save(update_fields=['date_download'])
            logger.info("Скачивание файла прошло успешно!")
            return create_file_response(file_path, filename)
    except Exception as e:
        logger.error(str(e))
        return create_response(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))


# получается
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def creating_link_to_the_file(request):
    try:
        if request.method == 'GET':
            # user_id = request.GET.get('user_id')
            file_id = request.GET.get('file_id')
            characters = string.ascii_letters + string.digits
            one_time_link = ''.join(random.choices(characters, k=int(LENGTH_OF_THE_DOWNLOAD_LINK)))
            File.objects.filter(pk=file_id).update(link_for_download=one_time_link)
            logger.info("Ссылка на скачивание создана")
            return create_response(status.HTTP_200_OK,
                                   'Создана ссылка на скачивание',
                                   True,
                                   {'link': one_time_link})
    except Exception as e:
        logger.error(str(e))
        return create_response(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))


# не проходит
@api_view(['GET'])
def download_file_from_link(request):
    try:
        if request.method == 'GET':
            one_time_link = request.GET.get('link')
            file = File.objects.get(link_for_download=one_time_link)
            file_path = f'{BASE_DIR_STORAGE}{file.file_path}'
            filename = file.file_name
            response = create_file_response(file_path, filename)
            # file.link_for_download = ''
            # file.save(update_fields=['link_for_download'])
            logger.info("Скачивание файла прошло успешно!")
            return create_response(status.HTTP_200_OK,
                                   "Скачивание файла прошло успешно!",
                                   True,
                                   {'file_name': file.file_name})
    except Exception as e:
        logger.error(str(e))
        return create_response(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))
