import random

import stripe
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models.functions import math
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from .bll import amount_calcultaion
# Create your views here.
from django.views.generic import TemplateView, ListView, DetailView, DeleteView
from django.views.generic.base import View

from src.website.forms import OrderForm
from src.website.models import Product, Category, Cart, CartItem, Order


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
        tax, total, total_amount, cart = amount_calcultaion(self.request)
        context['tax'] = tax
        context['total'] = total
        context['total_amount'] = total_amount
        context['cart'] = cart
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


class CheckOut(View):
    def get(self, request):
        form = OrderForm()
        tax, total, total_amount, cart_item = amount_calcultaion(self.request)
        context = {
            'total': total, 'total_amount': total_amount, 'cart_item': cart_item, 'tax': tax,
            'form': form
        }
        return render(self.request, 'website/checkout.html', context)

    def post(self, request):
        cart_item = CartItem.objects.filter(cart__user=self.request.user)
        if cart_item.count() <= 0:
            messages.error(request, 'Select Product to Purchase')
            return redirect('website:store')
        tax, total, total_amount, cart_item = amount_calcultaion(self.request)
        order = Order.objects.filter(user=self.request.user, is_ordered=False)
        order_number = random.randint(0, 999999999999)
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.ip = self.request.META.get('REMOTE_ADDR')
            data.order_note = form.cleaned_data['order_note']
            data.user = self.request.user
            data.product_tax = tax
            data.order_number = order_number
            data.order_total = total_amount
            data.save()
            order = Order.objects.get(user=self.request.user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'total': total,
                'tax': tax,
                'total_amount': total_amount,
                'cart_item': cart_item
            }
            return render(self.request, 'website/payment.html', context)
        return redirect('website:checkout')


class CreateCheckoutSessionView(View):

    def post(self, request, *args, **kwargs):
        stripe.api_key = 'sk_test_51LC794Js59MkLRK8jKm97MecFP4dwcOrxfetIXefvByCaodNGQ1qNdKqaxVBZGD1aW9VTBh69W73T1Ox7LtByRpy00nRXonBff '
        host = self.request.get_host()
        tax, total, total_amount, cart_item = amount_calcultaion(self.request)
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            customer_email=self.request.user.email,
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': int(total_amount * 100),
                        'product_data': {
                            'name': 'Purchase Product'

                        },
                    },
                    'quantity': 2,
                },
            ],

        mode='payment',
            success_url='http://{}{}'.format(host, reverse('website:success')),
            cancel_url='http://{}{}'.format(host, reverse('website:cancel')),
        )
        return redirect(checkout_session.url, code=303)


class SuccessPayment(TemplateView):
    template_name = 'website/success.html'


class CancelPayment(TemplateView):
    template_name = 'website/cancel.html'
