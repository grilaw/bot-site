
from django.urls import path, include

from django.conf.urls.static import static
from django.conf import settings

from . import views

urlpatterns = [
    path('', views.profile, name='profile'),
    path('panel', views.panel, name='adminpanel')
]
