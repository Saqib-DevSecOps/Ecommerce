from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

# Create your views here.
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.base import View

from src.website.models import Product, Category, Cart, CartItem


class HomeTemplateView(TemplateView):
    template_name = 'website/home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeTemplateView, self).get_context_data(**kwargs)
        context['product'] = Product.objects.order_by('-created_at').all()[:8]
        context['category'] = Category.objects.all()[:8]
        return context


class StoreListView(ListView):
    model = Product
    template_name = 'website/store.html'
    context_object_name = 'product'
    paginate_by = 2

    def get_context_data(self, **kwargs):
        context = super(StoreListView, self).get_context_data(**kwargs)
        context['total'] = Product.objects.all().count()
        context['category'] = Category.objects.all()
        return context


class ProductDetailByCategory(ListView):
    model = Product
    template_name = 'website/store.html'
    context_object_name = 'product'

    def get_queryset(self):
        pk = self.kwargs['pk']
        return Product.objects.filter(category__id=pk)

    def get_context_data(self, **kwargs):
        context = super(ProductDetailByCategory, self).get_context_data(**kwargs)
        pk = self.kwargs['pk']
        context['total'] = Product.objects.filter(category__id=pk).count()
        context['category'] = Category.objects.all()
        return context


class StoreDetailView(DetailView):
    model = Product
    template_name = 'website/store_detail.html'
    context_object_name = 'product'


class AddToCart(View):
    def get(self, request,pk):
        product = Product.objects.get(id=pk)
        try:
            cart = Cart.objects.get(user = self.request.user)
        except Cart.DoesNotExist:
            cart = Cart.objects.create(user = self.request.user)
            cart.save()
        try:
            cart_item = CartItem.objects.get(product=product,cart=cart)
            cart_item.quantity+=1
            cart_item.save()
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(product=product,cart=cart,quantity=1)
            cart_item.save()

        return redirect('website:cart')


class AddToCartListView(ListView):
    model = CartItem
    template_name = 'website/add_to_cart.html'

