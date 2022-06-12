from django.contrib import admin

# Register your models here.
from src.accounts.models import User

admin.site.register(User)