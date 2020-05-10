from django.shortcuts import render
from oth import models
import datetime
from django.contrib.auth.decorators import login_required

from django.shortcuts import HttpResponse

# Create your views here.

m_level = 1
f_user = ""
last = 100


@login_required
def index(request):
    user = request.user
    if user.is_authenticated:
        player = models.Player.objects.get(user_id=request.user.pk)
        try:
            level = models.Level.objects.get(l_number=player.max_level)
            return render(request, 'oth/level.html', {'player': player, 'level': level})
        except:
            global last
            if player.max_level > last:
                return render(request, 'oth/win.html', {'player': player})
            return render(request, 'oth/finish.html', {'player': player})
    return render(request, 'oth/oth.html')


def save_profile(backend, user, response, *args, **kwargs):
    if backend.name == 'google-oauth2':
        profile = user
        try:
            player = models.Player.objects.get(user=profile)
        except:
            player = models.Player(user=profile)
            player.timestamp = datetime.datetime.now()
            player.name = response.get('name')
            player.save()
