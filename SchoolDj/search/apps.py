from django.apps import AppConfig
from django.conf import settings

from yandex_music import Client

class SearchConfig(AppConfig):
    name = 'search'
    yandex_client = None
    
    def ready(self):
        token = settings.YANDEX_MUSIC_TOKEN
        if token:
            SearchConfig.yandex_client = Client(token).init()