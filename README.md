# mycloud
Light вариант облачного хранилища.
Здесь размещена серверная часть, фронтенд - https://github.com/Volivanmail/User_cloud_front

## Развертывание проекта на сервере reg.ru

Для развертывания проекта на сервере reg.ru, следуйте инструкциям ниже:

### Шаг 1: Получение доступа к серверу

1. Войдите в свой аккаунт на reg.ru.
2. Перейдите в раздел управления хостингом.

### Шаг 2: Подготовка сервера

1. Установите необходимые зависимости, такие как Python, pip, базу данныx PostgreSQL и т.д.
```
    sudo apt install python3-postgresql python3-pip python3-venv
```
### Шаг 3: Клонирование проекта

1. Склонируйте репозиторий вашего проекта на сервер.
```
   git clone <URL-репозитория>
```   

### Шаг 4: Настройка проекта

1. Создайте и активируйте виртуальное окружение.
```
   python3 -m venv env
   source env/bin/activate
```

2. Установите необходимые зависимости.
```
   pip install -r requirements.txt
```

3. Настройте файлы конфигурации settings.py для подключения к базе данных и других настроек.

 

### Шаг 5: Запуск проекта

1. Запустите сервер Django.
   
```
   python manage.py runserver 0.0.0.0:8000
```

2. Настройте веб-сервер (например, Nginx) для проксирования запросов к серверу Django.

## Запуск локально
___
1. Установка зависимостей
```
pip install -r requirements.txt
```
2. Проверьте файл конфигурации, измените конфигурацию почтового ящика и базы данных
```
# my_cloud_app/app_config.properties

DB_ENGINE=django.db.backends.postgresql_psycopg2
DB_NAME=название базы данных
DB_USER=пользователь в Postgres
DB_PASSWORD=пароль
DB_HOST=127.0.0.1
DB_PORT=5432


3.Создать структуру базы данных
```
python manage.py migrate
```
4. Создайте суперпользователя
```
python manage.py createsuperuser
```
5. Запустите локальный сервер
```
python manage.py runserver
```