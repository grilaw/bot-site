from . import views
from django.urls import path

urlpatterns = [
    path('', views.songqueue, name='songqueue'),
    path('<int:pk>', views.SongDetailView.as_view(), name='song-detail'),
    path('<int:pk>/delete', views.SongDeleteView.as_view(), name='song-delete')
]