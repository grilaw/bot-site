from allauth.headless.adapter import DefaultHeadlessAdapter
import dataclasses

@dataclasses.dataclass
class CustomUserData:
    id: int
    display: str
    avatar: str
    is_staff: bool

class CustomHeadlessAdapter(DefaultHeadlessAdapter):
    def get_user_dataclass(self):
        return CustomUserData

    def user_as_dataclass(self, user):
      request = self.request
      # Безопасно получаем профиль (на случай, если его ещё нет) 
      profile = getattr(user, 'profile', None)
      avatar_url = ''
      if profile and profile.avatar:
          avatar_url = request.build_absolute_uri(profile.avatar.url)


      return CustomUserData(
          id=user.id,
          display=user.username,
          is_staff=user.is_staff,
          avatar=avatar_url,
      )