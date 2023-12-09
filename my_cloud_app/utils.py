import mimetypes

from django.http import HttpResponse
from rest_framework.response import Response

from my_cloud_app.models import File


def create_file_response(file_path, filename):
    with open(file_path, 'r') as file:
        mime_type, _ = mimetypes.guess_type(file_path)
        response = HttpResponse(file, content_type=mime_type)
        response['Content-Disposition'] = "attachment; filename=%s" % filename
    return response


def create_response(status_code, message, success=False, data=None):
    response = {
        "status": status_code,
        "message": message,
        "success": success
    }

    if data:
        response["data"] = data
    return Response(status=status_code, data=response)


def create_message_for_upload_file(file_name, new_file_name):
    if File.objects.filter(file_name=file_name).exists():
        print(1)
        # return f'Файл {file_name} загружен как {new_file_name}'
        return f'File {file_name} is uploaded as file {new_file_name}'

    # return 'Файл успешно загружен'.encode()
    return 'The file was uploaded successfully'
