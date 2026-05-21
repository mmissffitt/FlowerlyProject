from .models import Cart


def cart_counter(request):
    """Добавляет количество товаров в корзине в контекст всех шаблонов"""
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            count = cart.total_items()
        except Cart.DoesNotExist:
            count = 0
    else:
        count = 0
    return {'cart_count': count}