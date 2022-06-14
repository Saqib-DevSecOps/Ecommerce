from django.contrib import admin

# Register your models here.
from src.website.models import Category, Product, Cart, CartItem,OrderItem,Order,Payment

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Payment)
