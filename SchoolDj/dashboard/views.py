from io import BytesIO
import random

from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from .forms import AvatarForm
from django.http import JsonResponse
from django.core.files.base import ContentFile
from django.contrib.admin.views.decorators import staff_member_required
from django.core.management import call_command
from songqueue.models import ReqSongs, SongPoll

from PIL import Image
import os

import logging

logger = logging.getLogger(__name__)

def make_square(image, size=200):
    """Преобразует изображение в квадрат 1:1 с обрезкой центра"""
    with Image.open(image) as img:
        # Получаем размеры
        width, height = img.size
        
        # Определяем размер меньшей стороны
        min_size = min(width, height)
        
        # Вычисляем координаты для центрированной обрезки
        left = (width - min_size) / 2
        top = (height - min_size) / 2
        right = (width + min_size) / 2
        bottom = (height + min_size) / 2
        
        # Обрезаем до квадрата
        img_cropped = img.crop((left, top, right, bottom))
        
        # Изменяем размер до нужного
        img_resized = img_cropped.resize((size, size), Image.Resampling.LANCZOS)

        return img_resized

def profile(request):
    return render(request, 'dashboard/profile.html')

@require_http_methods(['POST'])
def changeavatar(request):
    form = AvatarForm(request.POST, request.FILES)
    if form.is_valid():
        avatar_file = form.cleaned_data['avatar']

        resized = make_square(avatar_file)

        img_io = BytesIO()
        resized.save(img_io, format='webp', quality=85)
        img_io.seek(0)

        filename = f"{request.user.profile.uuid}.webp"

        request.user.profile.avatar.save(
            filename,
            ContentFile(img_io.getvalue()),
            save=True
        )

        return JsonResponse({'success': True, 'new_avatar_url': request.user.profile.avatar.url, 'message': 'Аватар успешно обновлен'})
    else:
        return JsonResponse({'success': False, 'errors': form.errors})
    
@staff_member_required
def panel(request):
    songs = SongPoll.objects.all().order_by('-id')
    return render(request, 'dashboard/panel.html', {'polls': songs, 'style': 'dashboard/css/panel.css'})

@staff_member_required
@require_http_methods(['POST'])
def startvote(request):
    try:
        song_count = ReqSongs.objects.all().count()
        
        if song_count == 0:
            return JsonResponse({'success': False, 'message': 'Нет песен для голосования'})
        
        nominated = []
        max_songs = min(5, song_count)  # Если песен меньше 5
        
        # Получаем ВСЕ ID песен
        all_ids = list(ReqSongs.objects.values_list('id', flat=True))
        song_count = len(all_ids)
        
        if song_count == 0:
            return JsonResponse({'success': False, 'message': 'Нет песен для голосования'})
        
        # Выбираем случайные ID (гарантированно существующие)
        max_songs = min(5, song_count)
        selected_ids = random.sample(all_ids, max_songs)  # Всегда существуют
        
        # Удаляем старые опросы
        SongPoll.objects.all().delete()
        
        # Создаем новый опрос
        poll = SongPoll.objects.create()
        
        # Добавляем все песни одной командой
        poll.songs.set(selected_ids)
        return JsonResponse({'success': True, 'message': 'Голосование запущено'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
    
