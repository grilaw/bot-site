from django.core.management.base import BaseCommand
from django.db import connection
from songqueue.models import ReqSongs, SongPoll, Vote

class Command(BaseCommand):
    help = 'Очищает все треки и сбрасывает ID'

    def add_arguments(self, parser):
        parser.add_argument('--table', type=str, help='Стол для удаления')

    def handle(self, *args, **options):
        self.stdout.write('Очистка данных...')
        
        table = options.get('table')

        # Удаляем все данные
        
        if table == 'songpoll':
            self.songpoll_clear()
        elif table == 'reqsongs':
            self.reqsongs_clear()
        elif table == 'vote':
            self.vote_clear()
        elif not table:
            self.songpoll_clear()
            self.reqsongs_clear()
            self.vote_clear()
        else:
            self.stdout.write(self.style.ERROR('Неизвестный стол'))
        
        self.stdout.write(self.style.SUCCESS('Данные удалены'))
        
    def vote_clear(self):
        Vote.objects.all().delete()
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='songqueue_vote'")

    def reqsongs_clear(self):
        ReqSongs.objects.all().delete()
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='songqueue_reqsongs';")

    def songpoll_clear(self):
        SongPoll.objects.all().delete()
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='songqueue_songpoll';")