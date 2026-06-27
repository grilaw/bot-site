from django.shortcuts import render
from django.http import HttpResponse

from songqueue.models import SongPoll

# Create your views here.

def index(request):
    poll = SongPoll.objects.filter(active=True).order_by('-id').first()
    return render(request, 'browser/index.html', {'active_poll': poll, 'style': 'browser/css/index.css'})

def about(request):
    return render(request, 'browser/about.html')
