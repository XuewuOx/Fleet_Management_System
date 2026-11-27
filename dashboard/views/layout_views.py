from django.shortcuts import render
import json
import os

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings


def layout(request):

    return render(
        request,
        'dashboard/layout/layout.html'
    )


def layout_edit(request):

    return render(
        request,
        'dashboard/layout/layout_edit.html'
    )


@csrf_exempt
def save_layout(request):

    if request.method != "POST":

        return JsonResponse({

            "status":"error",
            "message":"POST required"

        })

    try:

        data = json.loads(
            request.body
        )

        file_path = os.path.join(

            settings.BASE_DIR,

            "dashboard",
            "static",
            "json",

            "factory_layout.json"

        )

        with open(
            file_path,
            "w"
        ) as file:

            json.dump(
                data,
                file,
                indent=2
            )

        return JsonResponse({

            "status":"success"

        })

    except Exception as e:

        return JsonResponse({

            "status":"error",
            "message":str(e)

        })