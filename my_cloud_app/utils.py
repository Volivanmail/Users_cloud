import mimetypes

from django.http import HttpResponse
from django.utils.encoding import escape_uri_path
from rest_framework.response import Response

from my_cloud_app.models import File


def create_file_response(file_path, filename):
    with open(file_path, 'rb') as file:
        # cod = filename.encode('utf-8')
        # name = cod.decode('utf-8')
        # print(cod)
        # print(cod.decode('utf-8'))
        mime_type, _ = mimetypes.guess_type(file_path)
        response = HttpResponse(file.read(), content_type=mime_type)
        response['Content-Disposition'] = f"attachment; filename*=utf-8''{escape_uri_path(filename)}"
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
