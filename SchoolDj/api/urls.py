
from django.contrib import admin
from django.urls import path, include

from django.conf.urls.static import static
from django.conf import settings

from search.views import add
from dashboard.views import changeavatar, startvote

urlpatterns = [
    path('change-avatar', changeavatar, name='change-avatar'),
    path('add/<int:trackid>', add, name='add'),
    path('startvote', startvote, name='startvote')
]
