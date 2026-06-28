from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
# Create your models here.

class ReqSongs(models.Model):
    title = models.CharField('Название', max_length=200, default='Неизвестно')
    author = models.CharField('Автор', max_length=200, default='Неизвестно')
    album = models.CharField('Альбом', max_length=200, default='Неизвестно')
    duration = models.IntegerField('Длительность сек', default=0)
    cover = models.ImageField('Обложка альбома', default='browser/img/logo.jpg')
    requester = models.CharField('Заказал', default='Неизвестный', max_length=200)

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


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    song = models.ForeignKey(ReqSongs, on_delete=models.CASCADE)
    poll = models.ForeignKey(SongPoll, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('user', 'poll')