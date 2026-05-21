from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Review, Order, Flower, Decor, ReadyBouquet, PromoCode


# ============================================
# ФОРМЫ АВТОРИЗАЦИИ
# ============================================
class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class UserLoginForm(forms.Form):
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Введите email'})
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Введите пароль'})
    )


# ============================================
# ФОРМЫ ПРОФИЛЯ
# ============================================
class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone', 'default_address', 'avatar')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


# ============================================
# ФОРМА ОФОРМЛЕНИЯ ЗАКАЗА
# ============================================
class CheckoutForm(forms.Form):
    address = forms.CharField(
        label='Адрес доставки',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Город, улица, дом, квартира'
        })
    )
    delivery_date = forms.DateField(
        label='Дата доставки',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
        })
    )
    delivery_time_slot = forms.ChoiceField(
        label='Время доставки',
        choices=[
            ('', 'Выберите время...'),
            ('9-12', '09:00 – 12:00'),
            ('12-15', '12:00 – 15:00'),
            ('15-18', '15:00 – 18:00'),
            ('18-21', '18:00 – 21:00'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )
    comment = forms.CharField(
        label='Комментарий к заказу',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Дополнительные пожелания...'
        })
    )


class PromoCodeForm(forms.Form):
    code = forms.CharField(
        label='Промокод',
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите промокод'
        })
    )


# ============================================
# ФОРМА ОТЗЫВА
# ============================================
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('rating', 'text')
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, f'{i} ★') for i in range(1, 6)]),
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Расскажите о своих впечатлениях...'
            }),
        }


# ============================================
# АДМИН-ФОРМЫ ДЛЯ CRUD
# ============================================
class FlowerForm(forms.ModelForm):
    class Meta:
        model = Flower
        fields = ('category', 'name', 'price', 'image', 'description', 'available', 'is_popular')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-control'


class DecorForm(forms.ModelForm):
    class Meta:
        model = Decor
        fields = ('category', 'name', 'price', 'image', 'available')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-control'


class ReadyBouquetForm(forms.ModelForm):
    class Meta:
        model = ReadyBouquet
        fields = ('name', 'description', 'price', 'image', 'occasion', 'color_palette', 'available', 'is_hit')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-control'


class PromoCodeAdminForm(forms.ModelForm):
    class Meta:
        model = PromoCode
        fields = ('code', 'discount_type', 'discount_value', 'min_order_amount',
                   'valid_from', 'valid_to', 'usage_limit', 'is_active')
        widgets = {
            'valid_from': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'valid_to': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'