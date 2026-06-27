from django.db import models
from django.contrib.auth.models import User
import uuid

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    uuid = models.UUIDField(default=uuid.uuid1, editable=False, unique=True)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default-avatar.webp')

    def __str__(self):
        return f'Профиль пользователя: {(self.user.username)}'
    
    def save(self, *args, **kwargs):
        # Если аватар уже существует (обновление)
        if self.pk:
            try:
                old_avatar = UserProfile.objects.get(pk=self.pk).avatar
                # Если старый аватар существует и отличается от нового
                if old_avatar and old_avatar != self.avatar:
                    old_avatar.delete(save=False)
            except UserProfile.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)

