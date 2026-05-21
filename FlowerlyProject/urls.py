from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Стандартная админка Django (для крайних случаев)
    path('django-admin/', admin.site.urls),
    
    # Все маршруты нашего приложения
    path('', include('FlowerlyApp.urls')),
]

# В режиме разработки Django сам раздаёт медиа-файлы
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)