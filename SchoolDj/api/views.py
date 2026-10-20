import random
import logging

from django.db.models import Count

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from songqueue.models import Vote, SongPoll, ReqSongs

logger = logging.getLogger(__name__)

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

@api_view(["GET"])
def get_queue(request):
    queue = list(ReqSongs.objects.values())
    return Response(queue)

@api_view(['GET'])
def get_proposed(request):

    poll = SongPoll.objects.filter(active=True).order_by('-id').first()
    if not poll:
        return Response({
            "songs": []})

    songs = list(poll.songs.values('id', 'title', 'author', 'duration', 'cover', 'trackid', 'album'))
    return Response({
        "songs": songs,
    })

@api_view(['GET'])
def get_last_poll(request):
    
    last_poll = SongPoll.objects.filter(active=False).order_by('-id').first()

    if not last_poll:
        return Response({
            "status": "error",
            "message": "Нету голосований"
        })

    last_songs = list(last_poll.songs.values('id', 'title', 'author', 'duration', 'cover', 'trackid', 'album'))
    last_winner = last_poll.winner_id
    

    return Response({
        "last_songs": last_songs,
        "last_winner": last_winner,
    })


@api_view(['POST'])
def vote(request):
    logger.info(f"Пользователь {request.user.username} получил голос.")
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
    logger.info(f"get_votes: user={request.user}, auth={request.user.is_authenticated}")

    poll = SongPoll.objects.filter(active=True).last()
    if poll is None:
        return Response(
            {'status': 'error', 'message': 'Нет активного опроса'},
            status=status.HTTP_404_NOT_FOUND
        )

    user_vote = (
        Vote.objects
        .filter(poll=poll, user=request.user)
        .values_list('song_id', flat=True)
        .first()
        )

    votes_dict = votes(poll)
    return Response({'votes': votes_dict, 'user_vote': user_vote}, status=200)

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