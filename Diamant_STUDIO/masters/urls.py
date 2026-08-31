from django.urls import path
from .views import master_list, master_detail

urlpatterns = [
    path("", master_list, name="master_list"),

    path(
        "<int:pk>/",
        master_detail,
        name="master_detail",
    ),
]