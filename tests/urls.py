from django.http import HttpResponse
from django.urls import path

urlpatterns = [
    path("coffee/black/", lambda request: HttpResponse("a regular view")),
]
