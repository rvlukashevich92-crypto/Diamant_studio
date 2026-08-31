from django import forms
from django.contrib.auth.forms import UserCreationForm
from users.models import User


class ClientRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name")
