from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
# Create your models here.

class ReqSongs(models.Model):
    title = models.CharField('Название')
    author = models.CharField('Автор')
    album = models.CharField('Альбом')
    duration = models.IntegerField('Длительность сек')
    cover = models.ImageField('Обложка альбома', default='browser/img/logo.jpg')
    requester = models.CharField('Заказал', default='Неизвестный')

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('song-detail', args=[str(self.id)])

    class Meta:
        verbose_name = 'Заказанная песня'
        verbose_name_plural = 'Заказанные песни'
        # это то что отображается в админ панели

class SongPoll(models.Model):

    active = models.BooleanField('Активный', default=True)
    
    songs = models.ManyToManyField(
        ReqSongs,
        related_name='choosed',
        blank=True
    )

    users = models.ManyToManyField(
        User,
        related_name='votes',
        blank=True
    )