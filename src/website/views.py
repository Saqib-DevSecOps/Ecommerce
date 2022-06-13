from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect

# Create your views here.
from django.views.generic import TemplateView, ListView, DetailView, DeleteView
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

    def get_context_data(self, **kwargs):
        context = super(StoreDetailView, self).get_context_data(**kwargs)
        pk = self.kwargs['pk']
        context['in_cart'] = CartItem.objects.filter(product_id=pk, cart_id=self.request.user.id).exists()
        return context


class AddToCart(View):
    def get(self, request, pk):
        product = Product.objects.get(id=pk)
        try:
            cart = Cart.objects.get(user=self.request.user)
        except Cart.DoesNotExist:
            cart = Cart.objects.create(user=self.request.user)
            cart.save()
        try:
            cart_item = CartItem.objects.get(product=product, cart=cart)
            cart_item.quantity += 1
            cart_item.save()
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(product=product, cart=cart, quantity=1)
            cart_item.save()

        return redirect('website:cart')


class AddToCartListView(ListView):
    model = CartItem
    template_name = 'website/add_to_cart.html'
    context_object_name = 'cart'

    def get_queryset(self):
        cart_item = CartItem.objects.select_related('product').filter(cart__user=self.request.user)
        return cart_item

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(AddToCartListView, self).get_context_data(**kwargs)
        total = 0
        cart_items = 0

        cart_item = CartItem.objects.filter(cart__user=self.request.user)
        for cart in cart_item:
            total += cart.quantity * cart.product.price
            cart_items += cart.quantity
        tax = (2 * total) / 100
        total_amount = tax + total
        context['tax'] = tax
        context['total'] = total
        context['total_amount'] = total_amount
        context['cart'] = cart_item
        return context


class RemoveCart(View):
    def get(self, request, pk):
        cart = Cart.objects.get(user=self.request.user)
        product = Product.objects.get(id=pk)
        cart_item = CartItem.objects.get(cart=cart, product=product)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
        return redirect('website:cart')


class CartDelete(View):
    def get(self, request, pk):
        cart = Cart.objects.get(user=self.request.user)
        product = Product.objects.get(id=pk)
        cart_item = CartItem.objects.get(cart=cart, product=product)
        cart_item.delete()
        return redirect('website:cart')



