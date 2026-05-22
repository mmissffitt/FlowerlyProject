import json
from datetime import date, datetime, timedelta
from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse

from .models import (
    User, Category, Occasion, ColorPalette,
    Flower, Decor, ReadyBouquet, BouquetImage,
    CustomBouquet, CustomBouquetItem, CustomBouquetDecor,
    Cart, CartItem, PromoCode,
    Order, OrderItem, OrderStatusHistory,
    Favorite, Review,
)
from .forms import (
    UserRegisterForm, UserLoginForm, ProfileEditForm,
    CheckoutForm, PromoCodeForm, ReviewForm,
    FlowerForm, DecorForm, ReadyBouquetForm, PromoCodeAdminForm,
)


# ============================================================
# ДЕКОРАТОРЫ ДОСТУПА
# ============================================================
def florist_required(view_func):
    """Доступ только для флористов и администраторов"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('flowerly:login')
        if not (request.user.is_florist or request.user.is_staff):
            messages.error(request, 'Доступ запрещён')
            return redirect('flowerly:home')
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    """Доступ только для администраторов"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('flowerly:login')
        if not request.user.is_staff:
            messages.error(request, 'Доступ запрещён')
            return redirect('flowerly:home')
        return view_func(request, *args, **kwargs)
    return wrapper


# ============================================================
# 1. ОБЩИЕ СТРАНИЦЫ
# ============================================================
def home(request):
    """Главная страница"""
    hit_bouquets = ReadyBouquet.objects.filter(available=True, is_hit=True)[:8]
    popular_flowers = Flower.objects.filter(available=True, is_popular=True)[:6]
    new_bouquets = ReadyBouquet.objects.filter(available=True).order_by('-created_at')[:4]

    context = {
        'hit_bouquets': hit_bouquets,
        'popular_flowers': popular_flowers,
        'new_bouquets': new_bouquets,
    }
    return render(request, 'home.html', context)


def catalog(request):
    """Каталог готовых букетов с фильтрацией"""
    bouquets = ReadyBouquet.objects.filter(available=True).select_related('occasion', 'color_palette')

    # Фильтры
    occasion_slug = request.GET.get('occasion')
    color_slug = request.GET.get('color')
    sort = request.GET.get('sort', '-created_at')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if occasion_slug:
        bouquets = bouquets.filter(occasion__slug=occasion_slug)
    if color_slug:
        bouquets = bouquets.filter(color_palette__slug=color_slug)
    if min_price:
        bouquets = bouquets.filter(price__gte=min_price)
    if max_price:
        bouquets = bouquets.filter(price__lte=max_price)

    # Сортировка
    sort_options = {
        'price_asc': 'price',
        'price_desc': '-price',
        'name': 'name',
        'newest': '-created_at',
        'popular': '-is_hit',
    }
    bouquets = bouquets.order_by(sort_options.get(sort, '-created_at'))

    context = {
        'bouquets': bouquets,
        'occasions': Occasion.objects.all(),
        'colors': ColorPalette.objects.all(),
        'current_occasion': occasion_slug,
        'current_color': color_slug,
        'current_sort': sort,
        'current_min_price': min_price,
        'current_max_price': max_price,
    }
    return render(request, 'catalog/catalog.html', context)


def bouquet_detail(request, slug):
    """Карточка готового букета"""
    bouquet = get_object_or_404(
        ReadyBouquet.objects.select_related('occasion', 'color_palette').prefetch_related('extra_images'),
        slug=slug, available=True
    )
    reviews = bouquet.review_set.all().select_related('user').order_by('-created_at')
    extra_images = bouquet.extra_images.all()

    # Похожие букеты (тот же повод или цветовая гамма)
    similar = ReadyBouquet.objects.filter(available=True).exclude(id=bouquet.id)
    if bouquet.occasion:
        similar = similar.filter(occasion=bouquet.occasion)
    elif bouquet.color_palette:
        similar = similar.filter(color_palette=bouquet.color_palette)
    similar = similar[:4]

    # Проверяем, может ли пользователь оставить отзыв
    can_review = False
    user_review = None
    if request.user.is_authenticated:
        user_review = Review.objects.filter(user=request.user, ready_bouquet=bouquet).first()
        # Проверяем, покупал ли пользователь этот букет
        has_purchased = OrderItem.objects.filter(
            order__user=request.user,
            order__status='delivered',
            ready_bouquet=bouquet
        ).exists()
        can_review = has_purchased and not user_review

    # Проверяем, в избранном ли букет
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, ready_bouquet=bouquet).exists()

    context = {
        'bouquet': bouquet,
        'reviews': reviews,
        'extra_images': extra_images,
        'similar': similar,
        'can_review': can_review,
        'user_review': user_review,
        'is_favorite': is_favorite,
        'avg_rating': bouquet.average_rating(),
    }
    return render(request, 'catalog/bouquet_detail.html', context)


# ============================================================
# 2. АВТОРИЗАЦИЯ
# ============================================================
def user_register(request):
    """Регистрация нового пользователя"""
    if request.user.is_authenticated:
        return redirect('flowerly:home')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Создаём пустую корзину
            Cart.objects.create(user=user)
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.first_name}!')
            return redirect('flowerly:home')
    else:
        form = UserRegisterForm()

    return render(request, 'auth/register.html', {'form': form})


def user_login(request):
    """Вход в систему"""
    if request.user.is_authenticated:
        return redirect('flowerly:home')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                # Создаём корзину, если её нет
                Cart.objects.get_or_create(user=user)
                messages.success(request, f'С возвращением, {user.first_name}!')

                # Редирект на запрошенную страницу или на главную
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('flowerly:home')
            else:
                messages.error(request, 'Неверный email или пароль')
    else:
        form = UserLoginForm()

    return render(request, 'auth/login.html', {'form': form})


def user_logout(request):
    """Выход из системы"""
    logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('flowerly:home')


# ============================================================
# 3. КОНСТРУКТОР БУКЕТОВ
# ============================================================
def constructor(request):
    """Страница конструктора букетов"""
    flowers = Flower.objects.filter(available=True).select_related('category')
    decors = Decor.objects.filter(available=True).select_related('category')
    categories = Category.objects.all()

    # Получаем данные из сессии
    session_bouquet = request.session.get('constructor_bouquet', {
        'flowers': {},
        'decors': {},
        'notes': '',
    })

    # Считаем итоговую сумму
    total = 0
    for item in session_bouquet.get('flowers', {}).values():
        total += item['quantity'] * item['price']
    for item in session_bouquet.get('decors', {}).values():
        total += item['quantity'] * item['price']

    context = {
        'flowers': flowers,
        'decors': decors,
        'categories': categories,
        'session_bouquet': session_bouquet,
        'total': total,
    }
    return render(request, 'constructor/constructor.html', context)


@require_POST
def constructor_add_flower(request):
    data = json.loads(request.body)
    flower_id = str(data.get('flower_id'))
    quantity = int(data.get('quantity', 1))

    flower = get_object_or_404(Flower, id=flower_id, available=True)

    if 'constructor_bouquet' not in request.session:
        request.session['constructor_bouquet'] = {'flowers': {}, 'decors': {}, 'notes': ''}

    bouquet = request.session['constructor_bouquet']

    if flower_id in bouquet['flowers']:
        bouquet['flowers'][flower_id]['quantity'] += quantity
    else:
        bouquet['flowers'][flower_id] = {
            'name': flower.name,
            'price': float(flower.price),
            'quantity': quantity,
        }

    request.session.modified = True

    total = sum(v['quantity'] * v['price'] for v in bouquet['flowers'].values()) + \
            sum(v['quantity'] * v['price'] for v in bouquet['decors'].values())

    return JsonResponse({
        'success': True,
        'flowers': bouquet['flowers'],
        'decors': bouquet['decors'],
        'total': round(total, 2),
    })


@require_POST
def constructor_remove_flower(request):
    data = json.loads(request.body)
    flower_id = str(data.get('flower_id'))

    if 'constructor_bouquet' in request.session:
        bouquet = request.session['constructor_bouquet']
        if flower_id in bouquet.get('flowers', {}):
            del bouquet['flowers'][flower_id]
        request.session.modified = True

    total = sum(v['quantity'] * v['price'] for v in bouquet['flowers'].values()) + \
            sum(v['quantity'] * v['price'] for v in bouquet['decors'].values())

    return JsonResponse({
        'success': True,
        'flowers': bouquet['flowers'],
        'decors': bouquet['decors'],
        'total': round(total, 2),
    })

@require_POST
def constructor_add_decor(request):
    data = json.loads(request.body)
    decor_id = str(data.get('decor_id'))
    quantity = int(data.get('quantity', 1))

    decor = get_object_or_404(Decor, id=decor_id, available=True)

    if 'constructor_bouquet' not in request.session:
        request.session['constructor_bouquet'] = {'flowers': {}, 'decors': {}, 'notes': ''}

    bouquet = request.session['constructor_bouquet']

    if decor_id in bouquet['decors']:
        bouquet['decors'][decor_id]['quantity'] += quantity
    else:
        bouquet['decors'][decor_id] = {
            'name': decor.name,
            'price': float(decor.price),
            'quantity': quantity,
        }

    request.session.modified = True

    total = sum(v['quantity'] * v['price'] for v in bouquet['flowers'].values()) + \
            sum(v['quantity'] * v['price'] for v in bouquet['decors'].values())

    return JsonResponse({
        'success': True,
        'flowers': bouquet['flowers'],
        'decors': bouquet['decors'],
        'total': round(total, 2),
    })

@require_POST
def constructor_remove_decor(request):
    data = json.loads(request.body)
    decor_id = str(data.get('decor_id'))

    if 'constructor_bouquet' in request.session:
        bouquet = request.session['constructor_bouquet']
        if decor_id in bouquet.get('decors', {}):
            del bouquet['decors'][decor_id]
        request.session.modified = True

    total = sum(v['quantity'] * v['price'] for v in bouquet['flowers'].values()) + \
            sum(v['quantity'] * v['price'] for v in bouquet['decors'].values())

    return JsonResponse({
        'success': True,
        'flowers': bouquet['flowers'],
        'decors': bouquet['decors'],
        'total': round(total, 2),
    })

@login_required
@require_POST
def constructor_add_to_cart(request):
    """Добавление собранного букета в корзину"""
    session_bouquet = request.session.get('constructor_bouquet', {})

    if not session_bouquet.get('flowers') and not session_bouquet.get('decors'):
        messages.error(request, 'Добавьте хотя бы один цветок или декор')
        return redirect('flowerly:constructor')

    notes = request.POST.get('notes', '')

    # Создаём CustomBouquet
    custom_bouquet = CustomBouquet.objects.create(
        user=request.user,
        total_price=0,
        notes=notes
    )

    total = 0

    # Добавляем цветы
    for flower_id, item in session_bouquet.get('flowers', {}).items():
        flower = Flower.objects.get(id=flower_id)
        subtotal = item['quantity'] * flower.price
        CustomBouquetItem.objects.create(
            custom_bouquet=custom_bouquet,
            flower=flower,
            quantity=item['quantity'],
            price_at_moment=flower.price
        )
        total += subtotal

    # Добавляем декор
    for decor_id, item in session_bouquet.get('decors', {}).items():
        decor = Decor.objects.get(id=decor_id)
        subtotal = item['quantity'] * decor.price
        CustomBouquetDecor.objects.create(
            custom_bouquet=custom_bouquet,
            decor=decor,
            quantity=item['quantity'],
            price_at_moment=decor.price
        )
        total += subtotal

    # Обновляем итоговую цену
    custom_bouquet.total_price = total
    custom_bouquet.save()

    # Добавляем в корзину
    cart, _ = Cart.objects.get_or_create(user=request.user)
    CartItem.objects.create(
        cart=cart,
        custom_bouquet=custom_bouquet,
        quantity=1
    )

    # Очищаем сессию конструктора
    if 'constructor_bouquet' in request.session:
        del request.session['constructor_bouquet']
        request.session.modified = True

    messages.success(request, 'Ваш букет добавлен в корзину!')
    return redirect('flowerly:cart_detail')


# ============================================================
# 4. КОРЗИНА
# ============================================================
@login_required
def cart_detail(request):
    """Просмотр корзины"""
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all().select_related('ready_bouquet', 'custom_bouquet')

    # Проверяем доступность товаров
    unavailable_items = []
    for item in items:
        if item.ready_bouquet and not item.ready_bouquet.available:
            unavailable_items.append(item)
        elif item.custom_bouquet:
            # Проверяем цветы в собранном букете
            for flower_item in item.custom_bouquet.flower_items.all():
                if not flower_item.flower.available:
                    unavailable_items.append(item)
                    break

    total = cart.total_price()

    context = {
        'cart': cart,
        'items': items,
        'total': total,
        'unavailable_items': unavailable_items,
    }
    return render(request, 'cart/cart.html', context)


@login_required
@require_POST
def cart_update_quantity(request, item_id):
    """Обновление количества товара в корзине"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    quantity = int(request.POST.get('quantity', 1))

    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()

    return redirect('flowerly:cart_detail')


@login_required
def cart_remove_item(request, item_id):
    """Удаление товара из корзины"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.info(request, 'Товар удалён из корзины')
    return redirect('flowerly:cart_detail')


# ============================================================
# 5. ОФОРМЛЕНИЕ ЗАКАЗА
# ============================================================
@login_required
def checkout(request):
    """Оформление заказа"""
    cart = get_object_or_404(Cart, user=request.user)
    items = cart.items.all()

    if not items.exists():
        messages.warning(request, 'Ваша корзина пуста')
        return redirect('flowerly:cart_detail')

    # Предзаполняем адрес из профиля
    initial_data = {
        'address': request.user.default_address,
        'delivery_date': (date.today() + timedelta(days=1)).isoformat(),
    }

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            delivery_date = form.cleaned_data['delivery_date']

            # Валидация даты
            if delivery_date < date.today() + timedelta(days=1):
                messages.error(request, 'Дата доставки должна быть не раньше завтрашнего дня')
                return render(request, 'orders/checkout.html', {'form': form, 'cart': cart, 'items': items, 'total': cart.total_price()})

            if delivery_date > date.today() + timedelta(days=30):
                messages.error(request, 'Дата доставки не может быть позже чем через 30 дней')
                return render(request, 'orders/checkout.html', {'form': form, 'cart': cart, 'items': items, 'total': cart.total_price()})

            # Проверяем доступность всех товаров
            for item in items:
                if item.ready_bouquet and not item.ready_bouquet.available:
                    messages.error(request, f'Букет "{item.ready_bouquet.name}" больше не доступен')
                    return redirect('flowerly:cart_detail')

            # Рассчитываем скидку из сессии
            discount_amount = request.session.get('promo_discount', 0)
            promo_code = request.session.get('promo_code')
            promo = None
            if promo_code:
                try:
                    promo = PromoCode.objects.get(code=promo_code)
                except PromoCode.DoesNotExist:
                    pass

            # Создаём заказ
            total = cart.total_price()
            order = Order.objects.create(
            user=request.user,
            address=form.cleaned_data['address'],
            delivery_date=delivery_date,
            delivery_time_slot=form.cleaned_data['delivery_time_slot'],
            comment=form.cleaned_data['comment'],
            promo_code=promo,
            discount_amount=discount_amount,
            total_price=total - discount_amount,
            )

            # Переносим товары из корзины в заказ
            for item in items:
                price = item.get_price()
                OrderItem.objects.create(
                    order=order,
                    ready_bouquet=item.ready_bouquet,
                    custom_bouquet=item.custom_bouquet,
                    quantity=item.quantity,
                    price=price,
                )

            # Создаём запись в истории статусов
            OrderStatusHistory.objects.create(
                order=order,
                status='new',
                changed_by=request.user,
            )

            # Увеличиваем счётчик промокода
            if promo:
                promo.used_count += 1
                promo.save()

            # Очищаем корзину и данные промокода из сессии
            items.delete()
            if 'promo_code' in request.session:
                del request.session['promo_code']
            if 'promo_discount' in request.session:
                del request.session['promo_discount']
            request.session.modified = True

            messages.success(request, f'Заказ №{order.id} успешно оформлен!')
            return redirect('flowerly:order_success', order_id=order.id)

    else:
        form = CheckoutForm(initial=initial_data)

    context = {
        'form': form,
        'cart': cart,
        'items': items,
        'total': cart.total_price(),
        'promo_form': PromoCodeForm(),
    }
    return render(request, 'orders/checkout.html', context)


@login_required
@require_POST
def apply_promo(request):
    """Применение промокода"""
    form = PromoCodeForm(request.POST)
    if form.is_valid():
        code = form.cleaned_data['code'].upper()
        try:
            promo = PromoCode.objects.get(code=code)

            cart = Cart.objects.get(user=request.user)
            cart_total = cart.total_price()

            if promo.is_valid(cart_total):
                discount = promo.calculate_discount(cart_total)
                request.session['promo_code'] = code
                request.session['promo_discount'] = float(discount)
                request.session.modified = True
                messages.success(request, f'Промокод применён! Скидка: {discount:.2f} ₽')
            else:
                messages.error(request, 'Промокод недействителен или истёк')
        except PromoCode.DoesNotExist:
            messages.error(request, 'Промокод не найден')

    return redirect('flowerly:checkout')


@login_required
def order_success(request, order_id):
    """Страница успешного оформления заказа"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_success.html', {'order': order})


# ============================================================
# 6. ЛИЧНЫЙ КАБИНЕТ
# ============================================================
@login_required
def profile(request):
    """Личный кабинет"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    favorites = Favorite.objects.filter(user=request.user).count()
    total_orders = Order.objects.filter(user=request.user).count()

    context = {
        'orders': orders,
        'favorites_count': favorites,
        'total_orders': total_orders,
    }
    return render(request, 'profile/profile.html', context)


@login_required
def profile_edit(request):
    """Редактирование профиля"""
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлён')
            return redirect('flowerly:profile')
    else:
        form = ProfileEditForm(instance=request.user)

    return render(request, 'profile/profile_edit.html', {'form': form})


@login_required
def order_history(request):
    """История заказов"""
    status_filter = request.GET.get('status', '')
    orders = Order.objects.filter(user=request.user)

    if status_filter:
        orders = orders.filter(status=status_filter)

    orders = orders.order_by('-created_at')
    
    active_orders = orders.exclude(status__in=['delivered', 'cancelled'])
    completed_orders = orders.filter(status__in=['delivered', 'cancelled'])

    context = {
        'active_orders': active_orders,
        'completed_orders': completed_orders,
        'current_status': status_filter,
        'status_choices': Order.STATUS_CHOICES,
    }
    return render(request, 'profile/order_history.html', context)


@login_required
def order_detail(request, order_id):
    """Детали заказа"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = order.items.all()
    status_history = order.status_history.all()

    context = {
        'order': order,
        'items': items,
        'status_history': status_history,
    }
    return render(request, 'profile/order_detail.html', context)


@login_required
@require_POST
def cancel_order(request, order_id):
    """Отмена заказа покупателем"""
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if not order.can_be_cancelled():
        messages.error(request, 'Этот заказ уже нельзя отменить')
        return redirect('flowerly:order_detail', order_id=order.id)

    order.status = 'cancelled'
    order.save()

    OrderStatusHistory.objects.create(
        order=order,
        status='cancelled',
        changed_by=request.user,
    )

    messages.info(request, f'Заказ №{order.id} отменён')
    return redirect('flowerly:order_detail', order_id=order.id)


@login_required
def favorites(request):
    """Избранное"""
    favorites = Favorite.objects.filter(user=request.user).select_related('ready_bouquet')
    return render(request, 'profile/favorites.html', {'favorites': favorites})


@login_required
@require_POST
def toggle_favorite(request, bouquet_id):
    """Добавление/удаление из избранного"""
    bouquet = get_object_or_404(ReadyBouquet, id=bouquet_id)
    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        ready_bouquet=bouquet,
    )

    if not created:
        favorite.delete()
        is_favorite = False
    else:
        is_favorite = True

    return JsonResponse({
        'success': True,
        'is_favorite': is_favorite,
    })


@login_required
def my_reviews(request):
    """Мои отзывы"""
    reviews = Review.objects.filter(user=request.user).select_related('ready_bouquet')
    return render(request, 'profile/my_reviews.html', {'reviews': reviews})


@login_required
def add_review(request, bouquet_id):
    """Добавление отзыва"""
    bouquet = get_object_or_404(ReadyBouquet, id=bouquet_id)

    # Проверяем, покупал ли пользователь этот букет
    has_purchased = OrderItem.objects.filter(
        order__user=request.user,
        order__status='delivered',
        ready_bouquet=bouquet
    ).exists()

    if not has_purchased:
        messages.error(request, 'Вы можете оставить отзыв только на купленный букет')
        return redirect('flowerly:bouquet_detail', slug=bouquet.slug)

    # Проверяем, нет ли уже отзыва
    existing = Review.objects.filter(user=request.user, ready_bouquet=bouquet).first()
    if existing:
        messages.warning(request, 'Вы уже оставили отзыв на этот букет')
        return redirect('flowerly:bouquet_detail', slug=bouquet.slug)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.ready_bouquet = bouquet
            review.save()
            messages.success(request, 'Спасибо за отзыв!')
            return redirect('flowerly:bouquet_detail', slug=bouquet.slug)
    else:
        form = ReviewForm()

    return render(request, 'profile/add_review.html', {'form': form, 'bouquet': bouquet})


# ============================================================
# 7. ПАНЕЛЬ ФЛОРИСТА
# ============================================================
@florist_required
def florist_dashboard(request):
    """Рабочий стол флориста"""
    today = date.today()
    tomorrow = today + timedelta(days=1)

    today_orders = Order.objects.filter(
        delivery_date=today
    ).exclude(status__in=['cancelled', 'delivered']).order_by('delivery_time_slot')

    tomorrow_orders = Order.objects.filter(
        delivery_date=tomorrow
    ).exclude(status__in=['cancelled', 'delivered']).order_by('delivery_time_slot')

    active_orders_count = Order.objects.filter(
        status__in=['new', 'confirmed', 'assembling', 'ready', 'in_delivery']
    ).count()

    context = {
        'today_orders': today_orders,
        'tomorrow_orders': tomorrow_orders,
        'active_orders_count': active_orders_count,
    }
    return render(request, 'florist/dashboard.html', context)

@florist_required
def florist_orders(request):
    """Все заказы (для флориста)"""
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date', '')
    search = request.GET.get('search', '')

    orders = Order.objects.all().order_by('delivery_date', 'delivery_time_slot')

    if status_filter:
        orders = orders.filter(status=status_filter)
    if date_filter:
        orders = orders.filter(delivery_date=date_filter)
    if search:
        orders = orders.filter(id__icontains=search)

    context = {
        'orders': orders,
        'status_choices': Order.STATUS_CHOICES,
        'current_status': status_filter,
        'current_date': date_filter,
        'search': search,
    }
    return render(request, 'florist/orders.html', context)


@florist_required
def florist_order_detail(request, order_id):
    """Детали заказа для флориста"""
    order = get_object_or_404(Order, id=order_id)
    items = order.items.all()

    # Получаем состав собранных букетов
    for item in items:
        if item.custom_bouquet:
            item.flowers_list = item.custom_bouquet.flower_items.all()
            item.decors_list = item.custom_bouquet.decor_items.all()
            item.notes = item.custom_bouquet.notes

    context = {
        'order': order,
        'items': items,
        'status_history': order.status_history.all(),
        'allowed_transitions': Order.ALLOWED_TRANSITIONS.get(order.status, []),
    }
    return render(request, 'florist/order_detail.html', context)


@florist_required
@require_POST
def florist_change_status(request, order_id):
    """Смена статуса заказа флористом"""
    order = get_object_or_404(Order, id=order_id)
    new_status = request.POST.get('new_status')

    if not order.can_transition_to(new_status):
        messages.error(request, 'Невозможно изменить статус на выбранный')
        return redirect('flowerly:florist_order_detail', order_id=order.id)

    order.status = new_status
    order.save()

    OrderStatusHistory.objects.create(
        order=order,
        status=new_status,
        changed_by=request.user,
    )

    messages.success(request, f'Статус заказа №{order.id} изменён на "{order.get_status_display()}"')
    return redirect('flowerly:florist_order_detail', order_id=order.id)


@florist_required
def florist_availability(request):
    """Управление наличием цветов и декора"""
    flowers = Flower.objects.all().select_related('category')
    decors = Decor.objects.all().select_related('category')

    context = {
        'flowers': flowers,
        'decors': decors,
    }
    return render(request, 'florist/availability.html', context)


@florist_required
@require_POST
def florist_toggle_availability(request, item_type, item_id):
    """Переключение наличия товара"""
    if item_type == 'flower':
        item = get_object_or_404(Flower, id=item_id)
    elif item_type == 'decor':
        item = get_object_or_404(Decor, id=item_id)
    else:
        return JsonResponse({'success': False, 'error': 'Неверный тип'})

    item.available = not item.available
    item.save()

    return JsonResponse({
        'success': True,
        'available': item.available,
    })


# ============================================================
# 8. ПАНЕЛЬ АДМИНИСТРАТОРА
# ============================================================
@admin_required
def admin_dashboard(request):
    """Дашборд администратора"""
    today = date.today()
    month_start = today.replace(day=1)

    # Статистика
    today_orders_count = Order.objects.filter(created_at__date=today).count()
    active_orders_count = Order.objects.filter(
        status__in=['new', 'confirmed', 'assembling', 'ready', 'in_delivery']
    ).count()
    today_revenue = Order.objects.filter(
        created_at__date=today
    ).exclude(status='cancelled').aggregate(Sum('total_price'))['total_price__sum'] or 0
    month_revenue = Order.objects.filter(
        created_at__date__gte=month_start
    ).exclude(status='cancelled').aggregate(Sum('total_price'))['total_price__sum'] or 0

    # Заказы за последние 7 дней (для графика)
    last_7_days = []
    labels = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        count = Order.objects.filter(created_at__date=day).count()
        last_7_days.append(count)
        labels.append(day.strftime('%d.%m'))

    # Популярные букеты
    popular_bouquets = ReadyBouquet.objects.annotate(
        order_count=Count('orderitem')
    ).order_by('-order_count')[:5]

    context = {
        'today_orders_count': today_orders_count,
        'active_orders_count': active_orders_count,
        'today_revenue': today_revenue,
        'month_revenue': month_revenue,
        'chart_labels': json.dumps(labels),
        'chart_data': json.dumps(last_7_days),
        'popular_bouquets': popular_bouquets,
    }
    return render(request, 'admin_dashboard/dashboard.html', context)


# --- Управление цветами ---
@admin_required
def admin_flowers(request):
    """Список всех цветов"""
    flowers = Flower.objects.all().select_related('category')
    return render(request, 'admin_dashboard/flowers.html', {'flowers': flowers})


@admin_required
def admin_flower_add(request):
    """Добавление цветка"""
    if request.method == 'POST':
        form = FlowerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Цветок добавлен')
            return redirect('flowerly:admin_flowers')
    else:
        form = FlowerForm()
    return render(request, 'admin_dashboard/flower_form.html', {'form': form, 'action': 'Добавить'})


@admin_required
def admin_flower_edit(request, flower_id):
    """Редактирование цветка"""
    flower = get_object_or_404(Flower, id=flower_id)
    if request.method == 'POST':
        form = FlowerForm(request.POST, request.FILES, instance=flower)
        if form.is_valid():
            form.save()
            messages.success(request, 'Цветок обновлён')
            return redirect('flowerly:admin_flowers')
    else:
        form = FlowerForm(instance=flower)
    return render(request, 'admin_dashboard/flower_form.html', {'form': form, 'action': 'Редактировать'})


@admin_required
def admin_flower_delete(request, flower_id):
    """Удаление цветка"""
    flower = get_object_or_404(Flower, id=flower_id)
    flower.delete()
    messages.success(request, 'Цветок удалён')
    return redirect('flowerly:admin_flowers')


# --- Управление декором ---
@admin_required
def admin_decor(request):
    decors = Decor.objects.all().select_related('category')
    return render(request, 'admin_dashboard/decor.html', {'decors': decors})


@admin_required
def admin_decor_add(request):
    if request.method == 'POST':
        form = DecorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Декор добавлен')
            return redirect('flowerly:admin_decor')
    else:
        form = DecorForm()
    return render(request, 'admin_dashboard/decor_form.html', {'form': form, 'action': 'Добавить'})


@admin_required
def admin_decor_edit(request, decor_id):
    decor = get_object_or_404(Decor, id=decor_id)
    if request.method == 'POST':
        form = DecorForm(request.POST, request.FILES, instance=decor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Декор обновлён')
            return redirect('flowerly:admin_decor')
    else:
        form = DecorForm(instance=decor)
    return render(request, 'admin_dashboard/decor_form.html', {'form': form, 'action': 'Редактировать'})


@admin_required
def admin_decor_delete(request, decor_id):
    decor = get_object_or_404(Decor, id=decor_id)
    decor.delete()
    messages.success(request, 'Декор удалён')
    return redirect('flowerly:admin_decor')


# --- Управление букетами ---
@admin_required
def admin_bouquets(request):
    bouquets = ReadyBouquet.objects.all().select_related('occasion', 'color_palette')
    return render(request, 'admin_dashboard/bouquets.html', {'bouquets': bouquets})


@admin_required
def admin_bouquet_add(request):
    if request.method == 'POST':
        form = ReadyBouquetForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Букет добавлен')
            return redirect('flowerly:admin_bouquets')
    else:
        form = ReadyBouquetForm()
    return render(request, 'admin_dashboard/bouquet_form.html', {'form': form, 'action': 'Добавить'})


@admin_required
def admin_bouquet_edit(request, bouquet_id):
    bouquet = get_object_or_404(ReadyBouquet, id=bouquet_id)
    if request.method == 'POST':
        form = ReadyBouquetForm(request.POST, request.FILES, instance=bouquet)
        if form.is_valid():
            form.save()
            messages.success(request, 'Букет обновлён')
            return redirect('flowerly:admin_bouquets')
    else:
        form = ReadyBouquetForm(instance=bouquet)
    return render(request, 'admin_dashboard/bouquet_form.html', {'form': form, 'action': 'Редактировать'})


@admin_required
def admin_bouquet_delete(request, bouquet_id):
    bouquet = get_object_or_404(ReadyBouquet, id=bouquet_id)
    bouquet.delete()
    messages.success(request, 'Букет удалён')
    return redirect('flowerly:admin_bouquets')


# --- Управление заказами ---
@admin_required
def admin_orders(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'admin_dashboard/orders.html', {'orders': orders})


@admin_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    items = order.items.all()
    return render(request, 'admin_dashboard/order_detail.html', {
        'order': order,
        'items': items,
        'status_history': order.status_history.all(),
    })


@admin_required
def admin_cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    reason = request.POST.get('reason', '')
    order.status = 'cancelled'
    order.comment += f'\nПричина отмены: {reason}' if reason else ''
    order.save()
    OrderStatusHistory.objects.create(order=order, status='cancelled', changed_by=request.user)
    messages.info(request, f'Заказ №{order.id} отменён')
    return redirect('flowerly:admin_orders')


# --- Управление промокодами ---
@admin_required
def admin_promo(request):
    promos = PromoCode.objects.all()
    return render(request, 'admin_dashboard/promo.html', {'promos': promos})


@admin_required
def admin_promo_add(request):
    if request.method == 'POST':
        form = PromoCodeAdminForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Промокод создан')
            return redirect('flowerly:admin_promo')
    else:
        form = PromoCodeAdminForm()
    return render(request, 'admin_dashboard/promo_form.html', {'form': form, 'action': 'Создать'})


@admin_required
def admin_promo_edit(request, promo_id):
    promo = get_object_or_404(PromoCode, id=promo_id)
    if request.method == 'POST':
        form = PromoCodeAdminForm(request.POST, instance=promo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Промокод обновлён')
            return redirect('flowerly:admin_promo')
    else:
        form = PromoCodeAdminForm(instance=promo)
    return render(request, 'admin_dashboard/promo_form.html', {'form': form, 'action': 'Редактировать'})


@admin_required
def admin_promo_delete(request, promo_id):
    promo = get_object_or_404(PromoCode, id=promo_id)
    promo.delete()
    messages.success(request, 'Промокод удалён')
    return redirect('flowerly:admin_promo')


# --- Управление отзывами ---
@admin_required
def admin_reviews(request):
    reviews = Review.objects.all().select_related('user', 'ready_bouquet').order_by('-created_at')
    return render(request, 'admin_dashboard/reviews.html', {'reviews': reviews})


@admin_required
def admin_review_delete(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    review.delete()
    messages.success(request, 'Отзыв удалён')
    return redirect('flowerly:admin_reviews')

@login_required
def cart_add_bouquet(request, bouquet_id):
    """Добавление готового букета в корзину"""
    bouquet = get_object_or_404(ReadyBouquet, id=bouquet_id, available=True)
    
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Проверяем, есть ли уже такой букет в корзине
    existing = CartItem.objects.filter(cart=cart, ready_bouquet=bouquet).first()
    if existing:
        existing.quantity += 1
        existing.save()
        messages.success(request, f'Количество букета «{bouquet.name}» увеличено до {existing.quantity}')
    else:
        CartItem.objects.create(cart=cart, ready_bouquet=bouquet, quantity=1)
        messages.success(request, f'Букет «{bouquet.name}» добавлен в корзину')
    
    next_url = request.GET.get('next', '')
    if next_url == 'cart':
        return redirect('flowerly:cart_detail')
    referer = request.META.get('HTTP_REFERER', '')
    if referer:
     return redirect(referer)
    return redirect('flowerly:catalog')

def cart_count(request):
    """API для получения количества товаров в корзине"""
    count = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            count = cart.total_items()
        except Cart.DoesNotExist:
            pass
    return JsonResponse({'count': count})