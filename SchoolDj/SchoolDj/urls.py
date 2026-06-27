
from django.contrib import admin
from django.urls import path, include

from django.conf.urls.static import static
from django.conf import settings

from search import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('', include('browser.urls')),
    path('queue/', include('songqueue.urls')),
    path('accounts/', include('allauth.urls')),
    path('profile/', include('dashboard.urls')),
    path('search/', include('search.urls')),
    path('added', views.added, name='added')
] 

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)