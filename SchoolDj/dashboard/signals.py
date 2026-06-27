from django.db.models.signals import post_save
from django.dispatch import receiver
from allauth.socialaccount.models import SocialAccount
from .models import UserProfile
import requests
from django.core.files.base import ContentFile
from django.core.files import File
from django.contrib.auth.models import User

from allauth.socialaccount.models import SocialAccount

@receiver(post_save, sender=SocialAccount)
def save_yandex_avatar(sender, instance, created, **kwargs):
    if instance.provider == 'yandex':
        profile, created = UserProfile.objects.get_or_create(user=instance.user)
        
        avatar_id = instance.extra_data.get('default_avatar_id')
        if avatar_id:
            avatar_url = f'https://avatars.yandex.net/get-yapic/{avatar_id}/islands-200'
            
            # Скачиваем и сохраняем как файл
            response = requests.get(avatar_url)
            if response.status_code == 200:
                profile.avatar.save(
                    f'{instance.user.profile.uuid}.webp',
                    ContentFile(response.content),
                    save=True
                )

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Создаёт профиль при создании нового пользователя"""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Сохраняет профиль при сохранении пользователя"""
    instance.profile.save()