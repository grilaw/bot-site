from django.db.models import Count

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from songqueue.models import Vote, SongPoll, ReqSongs

# Перетащи сюда все апи херни дебик >:(

@api_view(['POST'])
def vote(request):

    if not request.user.is_authenticated:
        return Response({'status':401})
    
    song_id = request.data.get('songId')

    try:
        song = ReqSongs.objects.get(id=song_id)
    except ReqSongs.DoesNotExist:
        return Response({'status':404, 'message': 'Песня не найдена'})
    
    poll = SongPoll.objects.filter(active=True).last()

    if poll is None:
        return Response({'status':404, 'message': 'Ошибка, попробуйте позже'})
    
    if Vote.objects.filter(user=request.user, poll=poll).exists():
        return Response({
            'status': 'error',
            'message': 'Вы уже голосовали в этом опросе'
        }, status=status.HTTP_409_CONFLICT)
    
    if not poll.songs.filter(id=song_id).exists():
        return Response({'status':404, 'message': 'Песня не найдена в опросе'})

    Vote.objects.create(
        user=request.user,
        song=song,
        poll=poll
    )

    votes = (
        Vote.objects.filter(poll=poll)
        .values('song_id')
        .annotate(count=Count('id'))
    )
    
    # Преобразуем в словарь {song_id: count}
    votes_dict = {str(v['song_id']): v['count'] for v in votes}

    return Response({'status':201, 'votes': votes_dict})

@api_view(['GET'])
def get_votes(request):

    try:
        Vote.objects.get(user=request.user)
    except:
        return Response({'status':409, 'message': 'голос еще не отдан'})

    if not request.user.is_authenticated:
        return Response({'status':401})

    poll = SongPoll.objects.filter(active=True).last()
    if poll is None:
        return Response({
            'status': 'error',
            'message': 'Нет активного опроса'
        }, status=status.HTTP_404_NOT_FOUND)
    
    poll = SongPoll.objects.filter(active=True).last()
    votes = (
        Vote.objects.filter(poll=poll)
        .values('song_id')
        .annotate(count=Count('id'))
    )
    
    # Преобразуем в словарь {song_id: count}
    votes_dict = {str(v['song_id']): v['count'] for v in votes}

    return Response({'status':200, 'votes': votes_dict})