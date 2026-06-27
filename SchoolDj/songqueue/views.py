from django.shortcuts import render, redirect
from .models import ReqSongs
from django.views.generic import DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

# Create your views here.

def songqueue(request):
    songs = ReqSongs.objects.all().order_by('-id')
    return render(request, 'songqueue/queue.html', {'songs': songs, 'style': 'songqueue/css/songqueue.css'})

class SongDetailView(DetailView):
    model = ReqSongs
    template_name = 'songqueue/detail_view.html'
    context_object_name = 'song'

class SongDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView): 
    model = ReqSongs
    success_url = '/queue'
    template_name = 'songqueue/news-delete.html'

    def test_func(self):
        song = self.get_object()
        # Админ ИЛИ автор песни
        return self.request.user.is_staff or self.request.user == song.user
