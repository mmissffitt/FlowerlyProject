from django.urls import path
from . import views

app_name = 'flowerly'

urlpatterns = [
    # ============================================
    # ОБЩИЕ СТРАНИЦЫ (доступны всем)
    # ============================================
    path('', views.home, name='home'),
    path('catalog/', views.catalog, name='catalog'),
    path('catalog/<str:slug>/', views.bouquet_detail, name='bouquet_detail'),
    path('constructor/', views.constructor, name='constructor'),

    # ============================================
    # АВТОРИЗАЦИЯ
    # ============================================
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),

    # ============================================
    # AJAX-ЗАПРОСЫ
    # ============================================
    path('constructor/add-flower/', views.constructor_add_flower, name='constructor_add_flower'),
    path('constructor/remove-flower/', views.constructor_remove_flower, name='constructor_remove_flower'),
    path('constructor/add-decor/', views.constructor_add_decor, name='constructor_add_decor'),
    path('constructor/remove-decor/', views.constructor_remove_decor, name='constructor_remove_decor'),
    path('constructor/add-to-cart/', views.constructor_add_to_cart, name='constructor_add_to_cart'),
    path('favorite/toggle/<int:bouquet_id>/', views.toggle_favorite, name='toggle_favorite'),

    # ============================================
    # ЛИЧНЫЙ КАБИНЕТ (требуется авторизация)
    # ============================================
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/orders/', views.order_history, name='order_history'),
    path('profile/orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('profile/orders/<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
    path('profile/favorites/', views.favorites, name='favorites'),
    path('profile/reviews/', views.my_reviews, name='my_reviews'),
    path('profile/reviews/add/<int:bouquet_id>/', views.add_review, name='add_review'),

    # ============================================
    # КОРЗИНА И ОФОРМЛЕНИЕ
    # ============================================
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/update/<int:item_id>/', views.cart_update_quantity, name='cart_update'),
    path('cart/remove/<int:item_id>/', views.cart_remove_item, name='cart_remove'),
    path('cart/add/<int:bouquet_id>/', views.cart_add_bouquet, name='cart_add_bouquet'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/apply-promo/', views.apply_promo, name='apply_promo'),
    path('orders/<int:order_id>/success/', views.order_success, name='order_success'),

    # ============================================
    # ПАНЕЛЬ ФЛОРИСТА
    # ============================================
    path('florist/', views.florist_dashboard, name='florist_dashboard'),
    path('florist/orders/', views.florist_orders, name='florist_orders'),
    path('florist/orders/<int:order_id>/', views.florist_order_detail, name='florist_order_detail'),
    path('florist/orders/<int:order_id>/change-status/', views.florist_change_status, name='florist_change_status'),
    path('florist/availability/', views.florist_availability, name='florist_availability'),
    path('florist/availability/toggle/<str:item_type>/<int:item_id>/', views.florist_toggle_availability, name='florist_toggle_availability'),

    # ============================================
    # ПАНЕЛЬ АДМИНИСТРАТОРА
    # ============================================
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # Управление цветами
    path('admin-dashboard/flowers/', views.admin_flowers, name='admin_flowers'),
    path('admin-dashboard/flowers/add/', views.admin_flower_add, name='admin_flower_add'),
    path('admin-dashboard/flowers/<int:flower_id>/edit/', views.admin_flower_edit, name='admin_flower_edit'),
    path('admin-dashboard/flowers/<int:flower_id>/delete/', views.admin_flower_delete, name='admin_flower_delete'),

    # Управление декором
    path('admin-dashboard/decor/', views.admin_decor, name='admin_decor'),
    path('admin-dashboard/decor/add/', views.admin_decor_add, name='admin_decor_add'),
    path('admin-dashboard/decor/<int:decor_id>/edit/', views.admin_decor_edit, name='admin_decor_edit'),
    path('admin-dashboard/decor/<int:decor_id>/delete/', views.admin_decor_delete, name='admin_decor_delete'),

    # Управление букетами
    path('admin-dashboard/bouquets/', views.admin_bouquets, name='admin_bouquets'),
    path('admin-dashboard/bouquets/add/', views.admin_bouquet_add, name='admin_bouquet_add'),
    path('admin-dashboard/bouquets/<int:bouquet_id>/edit/', views.admin_bouquet_edit, name='admin_bouquet_edit'),
    path('admin-dashboard/bouquets/<int:bouquet_id>/delete/', views.admin_bouquet_delete, name='admin_bouquet_delete'),

    # Управление заказами
    path('admin-dashboard/orders/', views.admin_orders, name='admin_orders'),
    path('admin-dashboard/orders/<int:order_id>/', views.admin_order_detail, name='admin_order_detail'),
    path('admin-dashboard/orders/<int:order_id>/cancel/', views.admin_cancel_order, name='admin_cancel_order'),

    # Управление промокодами
    path('admin-dashboard/promo/', views.admin_promo, name='admin_promo'),
    path('admin-dashboard/promo/add/', views.admin_promo_add, name='admin_promo_add'),
    path('admin-dashboard/promo/<int:promo_id>/edit/', views.admin_promo_edit, name='admin_promo_edit'),
    path('admin-dashboard/promo/<int:promo_id>/delete/', views.admin_promo_delete, name='admin_promo_delete'),

    # Управление отзывами
    path('admin-dashboard/reviews/', views.admin_reviews, name='admin_reviews'),
    path('admin-dashboard/reviews/<int:review_id>/delete/', views.admin_review_delete, name='admin_review_delete'),
]