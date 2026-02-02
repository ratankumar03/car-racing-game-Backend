"""
URL configuration for racing_backend project.
"""
from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', lambda request: JsonResponse({
        'status': 'ok',
        'message': 'Racing Game API is running. See /api/health/'
    })),
    path('admin/', admin.site.urls),
    path('api/', include('racing_api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
