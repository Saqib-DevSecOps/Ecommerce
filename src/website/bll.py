from src.website.models import CartItem


def amount_calcultaion(request):
    total = 0
    cart_items = 0

    cart_item = CartItem.objects.filter(cart__user=request.user)
    for cart in cart_item:
        total += cart.quantity * cart.product.price
        cart_items += cart.quantity
    tax = (2 * total) / 100
    total_amount = tax + total
    return tax, total, total_amount, cart_item
