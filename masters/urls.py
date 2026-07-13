from django.urls import path
from .views import master_list

urlpatterns = [
    path("", master_list, name="master_list"),
]