from django.contrib import admin
from .models import User  

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "first_name", 
        "telegram_id", 
        "username",  
    )
    search_fields = (
        "username",
        "first_name",
    )

    ordering = (
        "username",
    )