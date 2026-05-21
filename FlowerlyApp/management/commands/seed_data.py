import random
from datetime import date, timedelta, time, datetime
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from FlowerlyApp.models import (
    User, Cart, Category, Occasion, ColorPalette,
    Flower, Decor, ReadyBouquet, BouquetImage,
    CustomBouquet, CustomBouquetItem, CustomBouquetDecor,
    CartItem, PromoCode, Order, OrderItem, OrderStatusHistory,
    Review, Favorite,
)


class Command(BaseCommand):
    help = 'Заполняет базу тестовыми данными'

    def handle(self, *args, **kwargs):
        self.stdout.write('🌱 Заполняю базу тестовыми данными...')

        # --- 1. Категории ---
        cat_flowers, _ = Category.objects.get_or_create(name='Цветы', slug='flowers')
        cat_greenery, _ = Category.objects.get_or_create(name='Зелень', slug='greenery')
        cat_decor, _ = Category.objects.get_or_create(name='Декор', slug='decor')

        # --- 2. Поводы ---
        occasions = []
        for name in ['День рождения', 'Свадьба', 'Юбилей', 'Без повода', 'Романтический']:
            obj, _ = Occasion.objects.get_or_create(name=name, slug=name.lower().replace(' ', '-'))
            occasions.append(obj)

        # --- 3. Цветовые гаммы ---
        palettes = []
        for name in ['Красный', 'Розовый', 'Белый', 'Жёлтый', 'Фиолетовый', 'Микс']:
            obj, _ = ColorPalette.objects.get_or_create(name=name, slug=name.lower())
            palettes.append(obj)

        # --- 4. Цветы ---
        flower_data = [
            ('Роза красная', cat_flowers, 250),
            ('Роза белая', cat_flowers, 270),
            ('Роза розовая', cat_flowers, 260),
            ('Пион розовый', cat_flowers, 300),
            ('Пион белый', cat_flowers, 320),
            ('Тюльпан жёлтый', cat_flowers, 120),
            ('Тюльпан красный', cat_flowers, 130),
            ('Тюльпан белый', cat_flowers, 125),
            ('Лилия белая', cat_flowers, 350),
            ('Лилия розовая', cat_flowers, 340),
            ('Гербера оранжевая', cat_flowers, 150),
            ('Гербера розовая', cat_flowers, 145),
            ('Хризантема белая', cat_flowers, 180),
            ('Орхидея белая', cat_flowers, 500),
            ('Подсолнух', cat_flowers, 200),
            ('Лаванда', cat_flowers, 160),
            ('Эустома белая', cat_flowers, 220),
            ('Альстромерия', cat_flowers, 140),
            ('Гвоздика красная', cat_flowers, 90),
            ('Гвоздика розовая', cat_flowers, 85),
        ]

        flowers = []
        for name, cat, price in flower_data:
            flower, _ = Flower.objects.get_or_create(
                name=name,
                defaults={
                    'category': cat,
                    'price': price,
                    'available': True,
                    'is_popular': random.choice([True, False]),
                    'description': f'Прекрасный {name.lower()} для вашего букета',
                }
            )
            flowers.append(flower)

        # --- 5. Зелень ---
        greenery_data = [
            ('Гипсофила', cat_greenery, 200),
            ('Эвкалипт', cat_greenery, 180),
            ('Папоротник', cat_greenery, 150),
            ('Рускус', cat_greenery, 140),
            ('Фисташка', cat_greenery, 170),
        ]

        greeneries = []
        for name, cat, price in greenery_data:
            greenery, _ = Flower.objects.get_or_create(
                name=name,
                defaults={
                    'category': cat,
                    'price': price,
                    'available': True,
                    'is_popular': False,
                }
            )
            greeneries.append(greenery)

        # --- 6. Декор ---
        decor_data = [
            ('Лента атласная', cat_decor, 150),
            ('Крафт-бумага', cat_decor, 100),
            ('Подарочная коробка', cat_decor, 500),
            ('Открытка', cat_decor, 80),
            ('Воздушный шар', cat_decor, 200),
            ('Бусы декоративные', cat_decor, 120),
        ]

        decors = []
        for name, cat, price in decor_data:
            decor, _ = Decor.objects.get_or_create(
                name=name,
                defaults={
                    'category': cat,
                    'price': price,
                    'available': True,
                }
            )
            decors.append(decor)

        # --- 7. Готовые букеты ---
        bouquet_data = [
            ('Нежность', 3500, occasions[4], palettes[1]),
            ('Страсть', 4200, occasions[4], palettes[0]),
            ('Свадебный', 5500, occasions[1], palettes[2]),
            ('Солнечный', 2800, occasions[0], palettes[3]),
            ('Юбилейный', 6000, occasions[2], palettes[5]),
            ('Лавандовый сон', 3800, occasions[3], palettes[4]),
            ('Классика', 3200, occasions[3], palettes[5]),
            ('Романтика', 4500, occasions[4], palettes[1]),
        ]

        bouquets = []
        for name, price, occasion, palette in bouquet_data:
            bouquet, _ = ReadyBouquet.objects.get_or_create(
                name=name,
                defaults={
                    'slug': name.lower().replace(' ', '-'),
                    'description': f'Великолепный букет «{name}» для особого случая. Состав: свежие цветы, стильная упаковка.',
                    'price': price,
                    'available': True,
                    'is_hit': random.choice([True, False]),
                    'occasion': occasion,
                    'color_palette': palette,
                }
            )
            bouquets.append(bouquet)

        # --- 8. Пользователи ---
        # Покупатели
        customers = []
        customer_data = [
            ('anna@mail.ru', 'Анна', 'Иванова', '+79001112233'),
            ('peter@mail.ru', 'Пётр', 'Смирнов', '+79002223344'),
            ('olga@mail.ru', 'Ольга', 'Петрова', '+79003334455'),
        ]

        for email, first, last, phone in customer_data:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': first,
                    'last_name': last,
                    'phone': phone,
                    'default_address': f'г. Москва, ул. Цветочная, д. {random.randint(1, 50)}, кв. {random.randint(1, 200)}',
                }
            )
            if created:
                user.set_password('customer123')
                user.save()
                Cart.objects.create(user=user)
            customers.append(user)

        # --- 9. Промокоды ---
        promos = []
        promo_data = [
            ('WELCOME10', 'percent', 10, None),
            ('SALE500', 'fixed', 500, 2000),
            ('LOVE20', 'percent', 20, 3000),
        ]

        for code, dtype, dvalue, min_amount in promo_data:
            promo, _ = PromoCode.objects.get_or_create(
                code=code,
                defaults={
                    'discount_type': dtype,
                    'discount_value': dvalue,
                    'min_order_amount': min_amount,
                    'valid_from': timezone.now() - timedelta(days=30),
                    'valid_to': timezone.now() + timedelta(days=60),
                    'usage_limit': 100,
                    'is_active': True,
                }
            )
            promos.append(promo)

        # --- 10. Заказы ---
        statuses = ['new', 'confirmed', 'assembling', 'ready', 'in_delivery', 'delivered', 'cancelled']

        for customer in customers:
            for i in range(random.randint(1, 3)):
                # Выбираем случайный статус
                status = random.choice(statuses)

                # Создаём заказ
                delivery_date = date.today() + timedelta(days=random.randint(-10, 10))
                if delivery_date < date.today() and status in ['new', 'confirmed', 'assembling', 'ready']:
                    status = random.choice(['delivered', 'cancelled'])

                order = Order.objects.create(
                    user=customer,
                    status=status,
                    address=customer.default_address,
                    delivery_date=delivery_date,
                    delivery_time_slot=random.choice(['9-12', '12-15', '15-18', '18-21']),
                    comment=random.choice(['', 'Позвонить за час', 'Оставить у двери', '']),
                    promo_code=random.choice([None] + promos),
                    discount_amount=0,
                    total_price=0,
                )

                # Добавляем 1-3 букета в заказ
                total = 0
                for _ in range(random.randint(1, 3)):
                    if random.choice([True, False]):
                        # Готовый букет
                        bouquet = random.choice(bouquets)
                        qty = 1
                        price = bouquet.price * qty
                        OrderItem.objects.create(
                            order=order,
                            ready_bouquet=bouquet,
                            quantity=qty,
                            price=price,
                        )
                        total += price
                    else:
                        # Собранный букет
                        custom = CustomBouquet.objects.create(
                            user=customer,
                            total_price=0,
                            notes=random.choice(['', 'Нежные тона', 'Без резких запахов', '']),
                        )

                        custom_total = 0
                        for _ in range(random.randint(2, 5)):
                            flower = random.choice(flowers + greeneries)
                            qty = random.randint(1, 5)
                            CustomBouquetItem.objects.create(
                                custom_bouquet=custom,
                                flower=flower,
                                quantity=qty,
                                price_at_moment=flower.price,
                            )
                            custom_total += flower.price * qty

                        if random.choice([True, False]):
                            decor = random.choice(decors)
                            CustomBouquetDecor.objects.create(
                                custom_bouquet=custom,
                                decor=decor,
                                quantity=1,
                                price_at_moment=decor.price,
                            )
                            custom_total += decor.price

                        custom.total_price = custom_total
                        custom.save()

                        OrderItem.objects.create(
                            order=order,
                            custom_bouquet=custom,
                            quantity=1,
                            price=custom_total,
                        )
                        total += custom_total

                # Применяем скидку промокода
                if order.promo_code:
                    order.discount_amount = order.promo_code.calculate_discount(total)
                    order.promo_code.used_count += 1
                    order.promo_code.save()

                order.total_price = total - order.discount_amount
                order.save()

                # История статусов
                OrderStatusHistory.objects.create(
                    order=order,
                    status='new',
                    changed_at=order.created_at - timedelta(hours=random.randint(1, 72)),
                )

                status_order = ['confirmed', 'assembling', 'ready', 'in_delivery', 'delivered']
                current_index = status_order.index(status) if status in status_order else -1

                for s in status_order[:current_index]:
                    OrderStatusHistory.objects.create(
                        order=order,
                        status=s,
                        changed_at=order.created_at + timedelta(hours=random.randint(1, 4)),
                    )

                # Отзывы для доставленных
                if status == 'delivered':
                    for item in order.items.all():
                        if item.ready_bouquet and random.choice([True, False]):
                            Review.objects.get_or_create(
                                user=customer,
                                ready_bouquet=item.ready_bouquet,
                                defaults={
                                    'rating': random.randint(3, 5),
                                    'text': random.choice([
                                        'Очень красивый букет! Спасибо!',
                                        'Свежие цветы, быстрая доставка.',
                                        'Понравилось, буду заказывать ещё.',
                                        'Отличный подарок, все в восторге!',
                                        'Хороший букет, но упаковка могла быть лучше.',
                                    ]),
                                }
                            )

                # Избранное
                if random.choice([True, False]):
                    Favorite.objects.get_or_create(
                        user=customer,
                        ready_bouquet=random.choice(bouquets),
                    )

        self.stdout.write(self.style.SUCCESS('✅ База заполнена тестовыми данными!'))
        self.stdout.write(f'   • Категорий: 3')
        self.stdout.write(f'   • Цветов и зелени: {len(flowers) + len(greeneries)}')
        self.stdout.write(f'   • Декора: {len(decors)}')
        self.stdout.write(f'   • Букетов: {len(bouquets)}')
        self.stdout.write(f'   • Покупателей: {len(customers)}')
        self.stdout.write(f'   • Промокодов: {len(promos)}')
        self.stdout.write(f'   • Заказов: {Order.objects.count()}')
        self.stdout.write(f'   • Отзывов: {Review.objects.count()}')
        self.stdout.write('')
        self.stdout.write('   🔑 Данные для входа:')
        self.stdout.write('      Админ: admin@flowerly.ru (ваш пароль)')
        self.stdout.write('      Флорист: florist@flowerly.ru / florist123')
        self.stdout.write('      Покупатель: anna@mail.ru / customer123')
        self.stdout.write('      Покупатель: peter@mail.ru / customer123')
        self.stdout.write('      Покупатель: olga@mail.ru / customer123')