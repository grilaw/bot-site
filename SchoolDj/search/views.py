import datetime

from django.shortcuts import render, redirect
from django.conf import settings
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from search.apps import SearchConfig
from songqueue.models import ReqSongs

# Create your views here.
@login_required
def search(request, query):

    if not query or query.strip() == '':
        return redirect('/')

    client = SearchConfig.yandex_client

    results = client.search(query, nocorrect=False)

    tracks = []
    if results.tracks:
        results = results.tracks.results
        for track in results:
            
            tracks.append({
                'id': track.id,
                'title': track.title,
                'author': ', '.join(artist.name for artist in track.artists),
                'album': track.albums[0].title,
                'duration': track.duration_ms // 1000,
                'artwork': f"https://{track.albums[0].cover_uri.replace('%%', '100x100')}" if track.albums[0].cover_uri else "static/browser/img/logo.jpg",
                'explicit': track.explicit
            })

    return render(request, 'search/search.html', {'query': query, 'tracks': tracks, 'style': 'search/css/search.css', 'max_duration': settings.MAX_DURATION})

@require_http_methods(["POST"])
def add(request, trackid):

    if not trackid:
        return redirect('/')
    
    client = SearchConfig.yandex_client

    track_info = client.tracks(trackid)[0]

    if track_info.duration_ms // 1000 > settings.MAX_DURATION or track_info.explicit:
        return redirect('/')

    cover_uri = track_info.albums[0].cover_uri
    cover = f"https://{cover_uri.replace('%%', '200x200')}"
    
    data = {
        'title': track_info.title,
        'author': ', '.join(artist.name for artist in track_info.artists),
        'album': track_info.albums[0].title,
        'duration': track_info.duration_ms // 1000,
        'cover': cover,
        'requester': request.user.profile.uuid
    }

    product, created = ReqSongs.objects.get_or_create(
        title=track_info.title,
        author=', '.join(artist.name for artist in track_info.artists),
        defaults=data
    )

    if not created:
        return redirect('/added?message=Такой трек уже есть')
    return redirect('/added?message=Успешно!')

def added(request):
    message = request.GET.get('message', '')
    return render(request, 'search/added.html', {'message': message})