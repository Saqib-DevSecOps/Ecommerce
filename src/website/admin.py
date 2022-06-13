from django.contrib import admin

# Register your models here.
from src.website.models import Category, Product, Cart, CartItem

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItem)
