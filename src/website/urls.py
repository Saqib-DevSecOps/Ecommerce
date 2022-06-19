from django.urls import path

from src.website import views

app_name = 'website'

urlpatterns = [
    # Home

    path('', views.HomeTemplateView.as_view(), name='home'),
    path('store/', views.StoreListView.as_view(), name='store'),
    path('store-detail/<str:pk>/', views.StoreDetailView.as_view(), name='stores'),
    path('store_category/<str:pk>/', views.ProductDetailByCategory.as_view(), name='category'),

    # Cart

    path('add-to-cart/<str:pk>/', views.AddToCart.as_view(), name="add_to_cart"),
    path('cart_list/', views.AddToCartListView.as_view(), name='cart'),
    path('remove-cart/<str:pk>/', views.RemoveCart.as_view(), name='remove_cart'),
    path('delete-cart/<str:pk>/', views.CartDelete.as_view(), name='delete_cart'),

    # Checkout and Payment

    path('checkout/', views.CheckOut.as_view(), name="checkout"),
    path('payment/', views.CreateCheckoutSessionView.as_view(), name="payment"),
    path('payment-success/', views.SuccessPayment.as_view(), name="success"),
    path('payment-cancelled/', views.CancelPayment.as_view(), name="cancel"),
]
