from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

# Кастомизация админки
admin.site.site_header = "Независимая экспертиза"
admin.site.site_title = "Админ-панель"
admin.site.index_title = "Управление сайтом"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    # Media files - serve in production
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
