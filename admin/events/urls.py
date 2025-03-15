from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from . import views

app_name = 'events'

urlpatterns = [
    path('', admin.site.urls),
    path('admin/log/', views.log_from_frontend, name='log_from_frontend'),
]

# Добавляем обработку статических и медиа файлов в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 