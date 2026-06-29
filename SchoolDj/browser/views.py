from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Case, When, Value, BooleanField

from songqueue.models import SongPoll, Vote

# Create your views here.

def index(request):
    poll = SongPoll.objects.filter(active=True).order_by('-id').first()

    if not poll:
        last_poll = SongPoll.objects.last()
        last_winner = last_poll.winner
        if last_winner:
            return render(request, 'browser/index.html', {
                'last_winner': last_winner,
                'style': 'browser/css/index.css' # надо бы это сделать внутри хтмл чтобы везде не писать
            })
        return render(request, 'browser/index.html', {
            'style': 'browser/css/index.css'
        })
    
    songs = poll.songs.all()
    if request.user.is_authenticated:
        user_choice = Vote.objects.filter(user=request.user, poll=poll).first()
        songs = poll.songs.annotate(
            is_voted=Case(
                When(id=user_choice.song.id if user_choice else None, then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            ),
            is_user_nomination=Case(
                When(requester=str(request.user.profile.uuid), then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            )
        )

    for song in songs:
        song_class = 'song'
        if hasattr(song, 'is_voted') and song.is_voted:
            song_class += ' voted'
        if hasattr(song, 'is_user_nomination') and song.is_user_nomination:
            song_class += ' user-nomination'
        song.song_class = song_class

    return render(request, 'browser/index.html', {'songs': songs, 'style': 'browser/css/index.css'})

def about(request):
    return render(request, 'browser/about.html')
