import requests
from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import User
from .models import UserProfile

DEFAULT_AVATAR = 'avatars/default-avatar.webp'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=SocialAccount)
def save_yandex_avatar(sender, instance, **kwargs):
    if instance.provider != 'yandex':
        return

    profile, _ = UserProfile.objects.get_or_create(user=instance.user)

    # Уже есть не-дефолтный аватар — не перезаписываем
    if profile.avatar.name != DEFAULT_AVATAR:
        return

    avatar_id = instance.extra_data.get('default_avatar_id')
    if not avatar_id:
        return

    url = f'https://avatars.yandex.net/get-yapic/{avatar_id}/islands-200'
    try:
        response = requests.get(url, timeout=5)
    except requests.RequestException:
        return

    if response.status_code == 200:
        profile.avatar.save(
            f'{profile.uuid}.webp',
            ContentFile(response.content),
            save=True,
        )


@receiver(post_delete, sender=UserProfile)
def delete_avatar_on_profile_delete(sender, instance, **kwargs):
    if instance.avatar and instance.avatar.name != DEFAULT_AVATAR:
        instance.avatar.delete(save=False)