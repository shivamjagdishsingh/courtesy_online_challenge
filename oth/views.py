from django.shortcuts import render
from oth import models
import datetime
from django.contrib.auth.decorators import login_required

from django.shortcuts import HttpResponse

# Create your views here.

m_level = 1
f_user = ""
last = 100


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


@login_required
def answer(request):
    ans = ""
    if request.method == 'POST':
        ans = request.POST.get('ans')
    player = models.Player.objects.get(user_id=request.user.pk)
    try:
        level = models.Level.objects.get(l_number=player.max_level)
    except:
        return render(request, 'oth/finish.html', {'player': player})
    # print answer
    # print level.answer
    if ans == level.answer:
        # print level.answer
        player.max_level = player.max_level + 1
        player.score = player.score + 10
        player.timestamp = datetime.datetime.now()
        level.numuser = level.numuser + 1
        level.accuracy = round(level.numuser / (float(level.numuser + level.wrong)), 2)
        level.save()
        # print level.numuser
        # print player.max_level
        global m_level
        global f_user
        # print f_user
        # print m_level
        if m_level < player.max_level:
            m_level = player.max_level
            f_user = player.name
        player.save()

        try:
            level = models.Level.objects.get(l_number=player.max_level)
            # return render(request, 'level_transition.html')
            return render(request, 'oth/level.html', {'player': player, 'level': level})
        except:
            return render(request, 'oth/level_transition.html')
            global last
            if player.max_level > last:
                return render(request, 'oth/win.html', {'player': player})
            return render(request, 'oth/finish.html', {'player': player})
    elif ans == "":
        pass

    else:
        level.wrong = level.wrong + 1
        level.save()

        # messages.error(request, "Wrong Answer!, Try Again")

    return render(request, 'oth/level.html', {'player': player, 'level': level})


@login_required
def lboard(request):
    p = models.Player.objects.order_by('-score', 'timestamp')
    cur_rank = 1

    for pl in p:
        pl.rank = cur_rank
        cur_rank += 1

    return render(request, 'oth/lboard.html', {'players': p})


@login_required()
def rules(request):
    return render(request, 'oth/index_page.html')
