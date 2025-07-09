from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import home_redirect


urlpatterns = [
    path('admin/', admin.site.urls),
    path('hotel/admin/', include('admin_panel.urls')),
    path('', home_redirect, name='home'),
    path('hotel/', include('hotel.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)