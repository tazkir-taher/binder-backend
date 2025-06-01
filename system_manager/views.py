import datetime

from django.shortcuts import render
from .models import ErrorLog

from django.contrib.auth.models import User, Group, Permission


from rest_framework_simplejwt.tokens import RefreshToken, AccessToken, UntypedToken
from django.contrib.auth.hashers import check_password

from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework import status
from rest_framework.response import Response

@api_view(['get'])
@authentication_classes([])
@permission_classes([])
def seeder(request):
    return Response({'msg': "properly done"})


def log(path, msg):
    try:
        trace = []
        tb = msg.__traceback__
        while tb is not None:
            trace.append({
                "filename": tb.tb_frame.f_code.co_filename,
                "name": tb.tb_frame.f_code.co_name,
                "lineno": tb.tb_lineno
            })
            tb = tb.tb_next
        ErrorLog.objects.create(endpoint=path, message=str(msg), trace=trace)
    except Exception:
        ErrorLog.objects.create(endpoint=path, message=str(msg))
