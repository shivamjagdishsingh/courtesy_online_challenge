from django.shortcuts import render
from oth import models
import datetime
from django.contrib.auth.decorators import login_required
import random
from django.shortcuts import redirect
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

            if player.level < 5:
                level = models.Question.objects.filter(module__module__icontains="demo")
            elif player.level < 10:
                level = models.Question.objects.filter(module__module__icontains="2")
            elif player.level < 15:
                level = models.Question.objects.filter(module__module__icontains="3")
            elif player.level < 20:
                level = models.Question.objects.filter(module__module__icontains="4")
            elif player.level < 25:
                level = models.Question.objects.filter(module__module__icontains="5")
            elif player.level < 30:
                level = models.Question.objects.filter(module__module__icontains="6")
            elif player.level < 35:
                level = models.Question.objects.filter(module__module__icontains="7")

            question = level[random.randrange(1, level.count())]

            while models.Answer.objects.filter(question__question=question).exists():
                question = level[random.randrange(1, level.count())]
            return render(request, 'oth/level.html', {'player': player, 'level': question})
        except:
            global last
            if player.level > last:
                return render(request, 'oth/win.html', {'player': player})
            return render(request, 'oth/finish.html', {'player': player})
    return render(request, 'oth/oth.html')


@login_required
def answer(request, **kwargs):
    ans = ""
    if request.method == 'POST':
        ans = request.POST.get('answer', '')
    player = models.Player.objects.get(user_id=request.user.pk)

    try:
        level = models.Answer.objects.filter(user=player).count()
    except:
        return render(request, 'oth/finish.html', {'player': player})

    question = models.Question.objects.get(pk=kwargs['pk'])
    answer, created = models.Answer.objects.update_or_create(user=player, question=question,
                                                             defaults={'answer': ans})
    # answer.image =
    # answer.sentiment =
    # answer.facial_expression =

    player.level = player.level + 1
    player.score = player.score + 10
    player.timestamp = datetime.datetime.now()
    question.numuser = question.numuser + 1
    # level.accuracy = round(level.numuser / (float(level.numuser + level.wrong)), 2)
    question.save()
    # print level.numuser
    # print player.max_level
    global m_level
    global f_user
    # print f_user
    # print m_level
    if m_level < player.level:
        m_level = player.level
        f_user = player.name
    player.save()
    return redirect('/')

    # index(request)
    # try:
    #     level = models..objects.get(leve=player.level)
    #     # return render(request, 'level_transition.html')
    # except:
    #     return render(request, 'oth/level_transition.html')
    # global last
    # if player.level > last:
    #     return render(request, 'oth/win.html', {'player': player})
    # return render(request, 'oth/finish.html', {'player': player})
    # elif ans == "":
    #     pass
    #
    # else:
    #     level.wrong = level.wrong + 1
    #     level.save()
    #
    #     # messages.error(request, "Wrong Answer!, Try Again")
    #
    # return render(request, 'oth/level.html', {'player': player, 'level': level})


@login_required
def lboard(request):
    players = models.Player.objects.order_by('-score', 'timestamp')
    cur_rank = 1
    for player in players:
        player.rank = cur_rank
        cur_rank += 1

    return render(request, 'oth/lboard.html', {'players': players})


@login_required()
def rules(request):
    return render(request, 'oth/index_page.html')
