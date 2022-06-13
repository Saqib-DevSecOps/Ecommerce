from django.views.generic import ListView
from django.views.generic.base import View

from src.website.models import Category


def menu_links(request):
    links = Category.objects.all()
    return dict(links=links)