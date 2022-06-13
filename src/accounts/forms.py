import random

from allauth.account.forms import SignupForm
from django.contrib.auth.forms import UserCreationForm

from src.accounts.models import User

class CustomSignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email','username']