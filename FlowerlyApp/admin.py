from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import (
    User, Category, Occasion, ColorPalette,
    Flower, Decor, ReadyBouquet, BouquetImage,
    CustomBouquet, CustomBouquetItem, CustomBouquetDecor,
    Cart, CartItem, PromoCode,
    Order, OrderItem, OrderStatusHistory,
    Favorite, Review,
)


# ============================================
# 1. ПОЛЬЗОВАТЕЛЬ
# ============================================
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'phone', 'is_florist', 'is_staff', 'created_at')
    list_filter = ('is_florist', 'is_staff', 'is_superuser', 'created_at')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    ordering = ('-created_at',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Личная информация', {'fields': ('first_name', 'last_name', 'phone', 'default_address', 'avatar')}),
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_florist', 'groups')}),
        ('Даты', {'fields': ('last_login', 'created_at')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'phone', 'password1', 'password2'),
        }),
    )

    readonly_fields = ('created_at', 'last_login')


# ============================================
# 2. СПРАВОЧНИКИ
# ============================================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Occasion)
class OccasionAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(ColorPalette)
class ColorPaletteAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


# ============================================
# 3. ЦВЕТЫ И ДЕКОР
# ============================================
@admin.register(Flower)
class FlowerAdmin(admin.ModelAdmin):
    list_display = ('image_preview', 'name', 'category', 'price', 'available', 'is_popular')
    list_filter = ('category', 'available', 'is_popular')
    search_fields = ('name', 'description')
    list_editable = ('price', 'available', 'is_popular')

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return '—'
    image_preview.short_description = 'Фото'


@admin.register(Decor)
class DecorAdmin(admin.ModelAdmin):
    list_display = ('image_preview', 'name', 'category', 'price', 'available')
    list_filter = ('category', 'available')
    search_fields = ('name',)
    list_editable = ('price', 'available')

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return '—'
    image_preview.short_description = 'Фото'


# ============================================
# 4. ГОТОВЫЕ БУКЕТЫ
# ============================================
class BouquetImageInline(admin.TabularInline):
    model = BouquetImage
    extra = 3
    fields = ('image', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" />', obj.image.url)
        return '—'
    image_preview.short_description = 'Предпросмотр'


@admin.register(ReadyBouquet)
class ReadyBouquetAdmin(admin.ModelAdmin):
    list_display = ('image_preview', 'name', 'price', 'occasion', 'color_palette', 'available', 'is_hit', 'avg_rating')
    list_filter = ('occasion', 'color_palette', 'available', 'is_hit')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [BouquetImageInline]
    list_editable = ('price', 'available', 'is_hit')

    fieldsets = (
        ('Основное', {
            'fields': ('name', 'slug', 'description', 'price')
        }),
        ('Изображения', {
            'fields': ('image',)
        }),
        ('Параметры', {
            'fields': ('occasion', 'color_palette', 'available', 'is_hit')
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return '—'
    image_preview.short_description = 'Фото'

    def avg_rating(self, obj):
        return f"{obj.average_rating():.1f} ★"
    avg_rating.short_description = 'Рейтинг'


# ============================================
# 5. КОНСТРУКТОР БУКЕТОВ
# ============================================
class CustomBouquetItemInline(admin.TabularInline):
    model = CustomBouquetItem
    extra = 0
    readonly_fields = ('price_at_moment', 'subtotal_display')
    fields = ('flower', 'quantity', 'price_at_moment', 'subtotal_display')

    def subtotal_display(self, obj):
        if obj.pk:
            return f"{obj.subtotal():.2f} ₽"
        return '—'
    subtotal_display.short_description = 'Сумма'


class CustomBouquetDecorInline(admin.TabularInline):
    model = CustomBouquetDecor
    extra = 0
    readonly_fields = ('price_at_moment', 'subtotal_display')
    fields = ('decor', 'quantity', 'price_at_moment', 'subtotal_display')

    def subtotal_display(self, obj):
        if obj.pk:
            return f"{obj.subtotal():.2f} ₽"
        return '—'
    subtotal_display.short_description = 'Сумма'


@admin.register(CustomBouquet)
class CustomBouquetAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'notes')
    readonly_fields = ('total_price', 'created_at')
    inlines = [CustomBouquetItemInline, CustomBouquetDecorInline]


# ============================================
# 6. КОРЗИНА
# ============================================
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('get_name', 'get_price', 'added_at')
    fields = ('get_name', 'quantity', 'get_price', 'added_at')

    def get_name(self, obj):
        return obj.get_name() if obj.pk else '—'
    get_name.short_description = 'Товар'

    def get_price(self, obj):
        return f"{obj.get_price():.2f} ₽" if obj.pk else '—'
    get_price.short_description = 'Сумма'


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_items', 'total_price_display', 'updated_at')
    search_fields = ('user__email',)
    inlines = [CartItemInline]

    def total_price_display(self, obj):
        return f"{obj.total_price():.2f} ₽"
    total_price_display.short_description = 'Сумма корзины'


# ============================================
# 7. ПРОМОКОДЫ
# ============================================
@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'used_count', 'usage_limit', 'is_active', 'valid_from', 'valid_to')
    list_filter = ('discount_type', 'is_active')
    search_fields = ('code',)
    list_editable = ('is_active',)


# ============================================
# 8. ЗАКАЗЫ
# ============================================
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('get_name', 'quantity', 'price')
    fields = ('get_name', 'quantity', 'price')

    def get_name(self, obj):
        return obj.get_name() if obj.pk else '—'
    get_name.short_description = 'Товар'


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ('status', 'changed_by', 'changed_at')
    fields = ('status', 'changed_by', 'changed_at')
    can_delete = False
    max_num = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_link', 'status_badge', 'total_price', 'delivery_date', 'created_at')
    list_filter = ('status', 'delivery_date', 'created_at')
    search_fields = ('id', 'user__email', 'address')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [OrderItemInline, OrderStatusHistoryInline]

    fieldsets = (
        ('Информация о заказе', {
            'fields': ('user', 'status', 'total_price', 'discount_amount', 'promo_code')
        }),
        ('Доставка', {
            'fields': ('address', 'delivery_date', 'delivery_time_from', 'delivery_time_to')
        }),
        ('Дополнительно', {
            'fields': ('comment', 'created_at', 'updated_at')
        }),
    )

    def user_link(self, obj):
        return format_html(
            '<a href="/admin/FlowerlyApp/user/{}/change/">{}</a>',
            obj.user.id, obj.user.email
        )
    user_link.short_description = 'Покупатель'

    def status_badge(self, obj):
        colors = {
            'new': '#3498db',
            'confirmed': '#2ecc71',
            'assembling': '#f39c12',
            'ready': '#9b59b6',
            'in_delivery': '#1abc9c',
            'delivered': '#27ae60',
            'cancelled': '#e74c3c',
        }
        color = colors.get(obj.status, '#95a5a6')
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 8px; border-radius: 4px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Статус'


# ============================================
# 9. ИЗБРАННОЕ
# ============================================
@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'ready_bouquet', 'created_at')
    search_fields = ('user__email', 'ready_bouquet__name')
    list_filter = ('created_at',)


# ============================================
# 10. ОТЗЫВЫ
# ============================================
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'ready_bouquet', 'stars', 'text_preview', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__email', 'ready_bouquet__name', 'text')
    readonly_fields = ('created_at',)

    def stars(self, obj):
        return '★' * obj.rating + '☆' * (5 - obj.rating)
    stars.short_description = 'Оценка'

    def text_preview(self, obj):
        return obj.text[:100] + '...' if len(obj.text) > 100 else obj.text
    text_preview.short_description = 'Текст отзыва'