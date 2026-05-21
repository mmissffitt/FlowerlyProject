# FlowerlyApp/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.conf import settings


# ============================================
# 1. ПОЛЬЗОВАТЕЛЬ (должен быть первым)
# ============================================
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField('Email', unique=True)
    phone = models.CharField('Телефон', max_length=20, blank=True)
    default_address = models.TextField('Адрес по умолчанию', blank=True)
    avatar = models.ImageField('Аватар', upload_to='avatars/', blank=True)
    is_florist = models.BooleanField('Флорист', default=False)
    created_at = models.DateTimeField('Дата регистрации', auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"


# ============================================
# 2. СПРАВОЧНИКИ КАТАЛОГА
# ============================================
class Category(models.Model):
    name = models.CharField('Название', max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Occasion(models.Model):
    name = models.CharField('Повод', max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Повод'
        verbose_name_plural = 'Поводы'

    def __str__(self):
        return self.name


class ColorPalette(models.Model):
    name = models.CharField('Цветовая гамма', max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Цветовая гамма'
        verbose_name_plural = 'Цветовые гаммы'

    def __str__(self):
        return self.name


# ============================================
# 3. ЦВЕТЫ И ДЕКОР (ссылаются на Category)
# ============================================
class Flower(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')
    name = models.CharField('Название', max_length=200)
    price = models.DecimalField('Цена за шт.', max_digits=10, decimal_places=2)
    image = models.ImageField('Фото', upload_to='flowers/')
    description = models.TextField('Описание', blank=True)
    available = models.BooleanField('В наличии', default=True)
    is_popular = models.BooleanField('Популярный', default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Цветок'
        verbose_name_plural = 'Цветы'

    def __str__(self):
        return f"{self.name} — {self.price} ₽"


class Decor(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')
    name = models.CharField('Название', max_length=200)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    image = models.ImageField('Фото', upload_to='decor/')
    available = models.BooleanField('В наличии', default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Декор'
        verbose_name_plural = 'Декор'

    def __str__(self):
        return f"{self.name} — {self.price} ₽"


# ============================================
# 4. ГОТОВЫЕ БУКЕТЫ
# ============================================
class ReadyBouquet(models.Model):
    name = models.CharField('Название', max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField('Описание')
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    image = models.ImageField('Главное фото', upload_to='bouquets/')
    available = models.BooleanField('В наличии', default=True)
    is_hit = models.BooleanField('Хит продаж', default=False)
    occasion = models.ForeignKey(Occasion, on_delete=models.SET_NULL, null=True, blank=True)
    color_palette = models.ForeignKey(ColorPalette, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Готовый букет'
        verbose_name_plural = 'Готовые букеты'

    def __str__(self):
        return f"{self.name} — {self.price} ₽"

    def average_rating(self):
        reviews = self.review_set.all()
        if reviews:
            return sum(r.rating for r in reviews) / reviews.count()
        return 0


class BouquetImage(models.Model):
    bouquet = models.ForeignKey(ReadyBouquet, on_delete=models.CASCADE, related_name='extra_images')
    image = models.ImageField('Доп. фото', upload_to='bouquets/extra/')

    class Meta:
        verbose_name = 'Фото букета'
        verbose_name_plural = 'Дополнительные фото'


# ============================================
# 5. КОНСТРУКТОР БУКЕТОВ
# ============================================
class CustomBouquet(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_price = models.DecimalField('Итоговая цена', max_digits=10, decimal_places=2)
    notes = models.TextField('Пожелания флористу', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Собранный букет'
        verbose_name_plural = 'Собранные букеты'

    def get_items_summary(self):
        items = []
        for item in self.flower_items.all():
            items.append(f"{item.flower.name} ×{item.quantity}")
        for decor in self.decor_items.all():
            items.append(f"{decor.decor.name} ×{decor.quantity}")
        return ", ".join(items)


class CustomBouquetItem(models.Model):
    custom_bouquet = models.ForeignKey(CustomBouquet, on_delete=models.CASCADE, related_name='flower_items')
    flower = models.ForeignKey(Flower, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField('Количество')
    price_at_moment = models.DecimalField('Цена на момент добавления', max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Цветок в собранном букете'
        verbose_name_plural = 'Цветы в собранных букетах'

    def subtotal(self):
        return self.quantity * self.price_at_moment


class CustomBouquetDecor(models.Model):
    custom_bouquet = models.ForeignKey(CustomBouquet, on_delete=models.CASCADE, related_name='decor_items')
    decor = models.ForeignKey(Decor, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField('Количество')
    price_at_moment = models.DecimalField('Цена на момент добавления', max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Декор в собранном букете'
        verbose_name_plural = 'Декор в собранных букетах'

    def subtotal(self):
        return self.quantity * self.price_at_moment


# ============================================
# 6. КОРЗИНА
# ============================================
class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

    def total_price(self):
        return sum(item.get_price() for item in self.items.all())

    def total_items(self):
        return self.items.count()


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    ready_bouquet = models.ForeignKey(ReadyBouquet, on_delete=models.CASCADE, null=True, blank=True)
    custom_bouquet = models.ForeignKey(CustomBouquet, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField('Количество', default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Элемент корзины'
        verbose_name_plural = 'Элементы корзины'

    def clean(self):
        if self.ready_bouquet and self.custom_bouquet:
            raise ValidationError('Элемент может содержать либо готовый, либо собранный букет')
        if not self.ready_bouquet and not self.custom_bouquet:
            raise ValidationError('Должен быть указан букет')

    def get_price(self):
        if self.ready_bouquet:
            return self.ready_bouquet.price * self.quantity
        return self.custom_bouquet.total_price * self.quantity

    def get_name(self):
        if self.ready_bouquet:
            return self.ready_bouquet.name
        return f"Ваш букет №{self.custom_bouquet.id}"

    def get_image(self):
        if self.ready_bouquet:
            return self.ready_bouquet.image
        # Для собранного букета — первое изображение первого цветка
        first_flower = self.custom_bouquet.flower_items.first()
        if first_flower:
            return first_flower.flower.image
        return None


# ============================================
# 7. ПРОМОКОДЫ (нужны до Order)
# ============================================
class PromoCode(models.Model):
    DISCOUNT_TYPES = [
        ('percent', 'Процент'),
        ('fixed', 'Фиксированная сумма'),
    ]

    code = models.CharField('Код', max_length=50, unique=True)
    discount_type = models.CharField('Тип скидки', max_length=10, choices=DISCOUNT_TYPES)
    discount_value = models.DecimalField('Значение', max_digits=10, decimal_places=2)
    min_order_amount = models.DecimalField('Мин. сумма заказа', max_digits=10, decimal_places=2, null=True, blank=True)
    valid_from = models.DateTimeField('Действует с')
    valid_to = models.DateTimeField('Действует до')
    usage_limit = models.PositiveIntegerField('Лимит использований', null=True, blank=True)
    used_count = models.PositiveIntegerField('Использовано', default=0)
    is_active = models.BooleanField('Активен', default=True)

    class Meta:
        verbose_name = 'Промокод'
        verbose_name_plural = 'Промокоды'

    def __str__(self):
        return f"{self.code} ({self.get_discount_type_display()})"

    def is_valid(self, order_amount=None):
        from django.utils import timezone
        now = timezone.now()

        if not self.is_active:
            return False
        if self.valid_from and now < self.valid_from:
            return False
        if self.valid_to and now > self.valid_to:
            return False
        if self.usage_limit and self.used_count >= self.usage_limit:
            return False
        if self.min_order_amount and order_amount and order_amount < self.min_order_amount:
            return False
        return True

    def calculate_discount(self, amount):
        if self.discount_type == 'percent':
            return amount * self.discount_value / 100
        return min(self.discount_value, amount)


# ============================================
# 8. ЗАКАЗЫ
# ============================================
class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('confirmed', 'Принят'),
        ('assembling', 'Собирается'),
        ('ready', 'Готов'),
        ('in_delivery', 'В доставке'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменён'),
    ]

    ALLOWED_TRANSITIONS = {
        'new': ['confirmed', 'cancelled'],
        'confirmed': ['assembling', 'cancelled'],
        'assembling': ['ready'],
        'ready': ['in_delivery'],
        'in_delivery': ['delivered'],
    }

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='new')
    address = models.TextField('Адрес доставки')
    delivery_date = models.DateField('Дата доставки')
    delivery_time_slot = models.CharField('Слот доставки', max_length=20, choices=[
    ('9-12', '09:00 – 12:00'),
    ('12-15', '12:00 – 15:00'),
    ('15-18', '15:00 – 18:00'),
    ('18-21', '18:00 – 21:00'),
    ], default='9-12')
    comment = models.TextField('Комментарий', blank=True)
    promo_code = models.ForeignKey(PromoCode, on_delete=models.SET_NULL, null=True, blank=True)
    discount_amount = models.DecimalField('Скидка', max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField('Итоговая сумма', max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f"Заказ №{self.id} — {self.user.email} ({self.get_status_display()})"

    def can_be_cancelled(self):
        return self.status in ['new', 'confirmed']

    def can_transition_to(self, new_status):
        return new_status in self.ALLOWED_TRANSITIONS.get(self.status, [])


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    ready_bouquet = models.ForeignKey(ReadyBouquet, on_delete=models.SET_NULL, null=True, blank=True)
    custom_bouquet = models.ForeignKey(CustomBouquet, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField('Количество', default=1)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'

    def get_name(self):
        if self.ready_bouquet:
            return self.ready_bouquet.name
        return f"Ваш букет №{self.custom_bouquet.id}"


class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField('Статус', max_length=20, choices=Order.STATUS_CHOICES)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'История статуса'
        verbose_name_plural = 'История статусов'
        ordering = ['changed_at']


# ============================================
# 9. ИЗБРАННОЕ
# ============================================
class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ready_bouquet = models.ForeignKey(ReadyBouquet, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        unique_together = ('user', 'ready_bouquet')

    def __str__(self):
        return f"{self.user.email} → {self.ready_bouquet.name}"


# ============================================
# 10. ОТЗЫВЫ
# ============================================
class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ready_bouquet = models.ForeignKey(ReadyBouquet, on_delete=models.CASCADE)
    rating = models.IntegerField('Оценка', choices=[(i, str(i)) for i in range(1, 6)])
    text = models.TextField('Отзыв')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        unique_together = ('user', 'ready_bouquet')

    def __str__(self):
        return f"Отзыв от {self.user.first_name} на {self.ready_bouquet.name} — {self.rating}★"