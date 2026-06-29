import random

from django.db.models import Count

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from songqueue.models import Vote, SongPoll, ReqSongs

# Перетащи сюда все апи херни дебик >:(

def votes(poll):
    votes = (
        Vote.objects.filter(poll=poll)
        .values('song_id')
        .annotate(count=Count('id'))
    )
    
    # Преобразуем в словарь {song_id: count}
    votes_dict = {str(v['song_id']): v['count'] for v in votes}

    return votes_dict

@api_view(['POST'])
def vote(request):

    if not request.user.is_authenticated:
        return Response(status=401)
    
    song_id = request.data.get('songId')

    try:
        song = ReqSongs.objects.get(id=song_id)
    except ReqSongs.DoesNotExist:
        return Response({'message': 'Песня не найдена'}, status=404)
    
    poll = SongPoll.objects.filter(active=True).last()

    if poll is None:
        return Response({'message': 'Опрос не найден'}, status=404)
    
    if Vote.objects.filter(user=request.user, poll=poll).exists():
        return Response({
            'status': 'error',
            'message': 'Вы уже голосовали в этом опросе'
        }, status=409)
    
    if not poll.songs.filter(id=song_id).exists():
        return Response({'message': 'Песня не найдена в опросе'}, status=404)

    Vote.objects.create(
        user=request.user,
        song=song,
        poll=poll
    )

    votes_dict = votes(poll)

    return Response({'votes': votes_dict}, status=201)

@api_view(['GET'])
def get_votes(request):

    try:
        Vote.objects.get(user=request.user)
    except:
        return Response(status=409)

    if not request.user.is_authenticated:
        return Response(status=401)

    poll = SongPoll.objects.filter(active=True).last()
    if poll is None:
        return Response({
            'status': 'error',
            'message': 'Нет активного опроса'
        }, status=status.HTTP_404_NOT_FOUND)
    
    votes_dict = votes(poll)

    return Response({'votes': votes_dict}, status=200)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def finishvote(request):
    active_poll = SongPoll.objects.filter(active=True).last()
    if not active_poll:
        return Response({'message':'Нету голосования, для завершения'}, status=409)
    
    votes = (
        Vote.objects.filter(poll=active_poll)
        .values('song_id')
        .annotate(votes_count=Count('id'))
        .order_by('-votes_count')
    )
    if not votes:
        return Response({'message': 'Нету голосов, чтобы заканчивать'}, status=404)
    
    max_votes = votes.first()['votes_count']
    winner_votes = list(votes.filter(votes_count=max_votes))
    if len(winner_votes) > 1:
        winner_vote = random.choice(winner_votes)
    else:
        winner_vote = winner_votes[0]

    winner_song = ReqSongs.objects.get(id=winner_vote['song_id'])

    active_poll.winner = winner_song
    active_poll.active = False
    active_poll.save()
    
    return Response(status=200)