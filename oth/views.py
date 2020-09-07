from django.shortcuts import render
from oth import models
import datetime
from django.contrib.auth.decorators import login_required
import random
from django.shortcuts import redirect
from textblob import TextBlob
from django.http.response import StreamingHttpResponse
from oth.camera import VideoCamera
from django.shortcuts import HttpResponse

# Create your views here.

m_level = 1
f_user = ""
last = 100


def get_emotion(player):
    oneday = datetime.datetime.now() - datetime.timedelta(days=1)
    emotion_shivam = models.Emotion.objects.filter(user=player, timestamp__gt=oneday)
    if emotion_shivam:
        emotion_list = [emotion.emotion for emotion in emotion_shivam]
        bb = dict(zip(emotion_list, [emotion_list.count(i) for i in emotion_list]))
        final_emotion = max(bb, key=bb.get)
        player.player_emotion = final_emotion
        player.save()



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


def sentiment(text):
    obj = TextBlob(text)
    polarity = obj.sentiment.polarity
    label = ''
    if -1 <= polarity < -0.5:
        label = 'very bad'
    elif -0.5 <= polarity < -0.1:
        label = 'bad'
    elif -0.1 <= polarity < 0.2:
        label = 'ok'
    elif 0.2 <= polarity < 0.6:
        label = 'good'
    elif 0.6 <= polarity <= 1:
        label = 'positive'

    return label


@login_required
def index(request):
    user = request.user
    if user.is_authenticated:
        player = models.Player.objects.get(user_id=request.user.pk)
        get_emotion(player)
        if player.level >= 35:
            return redirect('oth:stay_tuned')

        if player.random_number == 1:
            random_number = models.Question.objects.last().id
            question = models.Question.objects.get(pk=random_number)
        else:
            question = models.Question.objects.get(pk=player.random_number)
        return render(request, 'oth/level.html', {'player': player, 'level': question})
    #     except:
    #         global last
    #         if player.level > last:
    #             return render(request, 'oth/win.html', {'player': player})
    #         return render(request, 'oth/stay_tuned.html', {'player': player})
    # return render(request, 'oth/oth.html')


@login_required
def answer(request, **kwargs):
    ans = ""
    if request.method == 'POST':
        ans = request.POST.get('answer', '')
    player = models.Player.objects.get(user_id=request.user.pk)

    get_emotion(player)
    if not 'happy'.__eq__(player.player_emotion):
        return redirect('oth:not_happy')
    # if (datetime.datetime.now(datetime.timezone.utc) - player.timestamp).days < 1:
    #     seconds = 86400 - (datetime.datetime.now(datetime.timezone.utc) - player.timestamp).total_seconds()
    #     seconds = seconds % (24 * 3600)
    #     hour = seconds // 3600
    #     seconds %= 3600
    #     minutes = seconds // 60
    #     seconds %= 60
    #
    #     return render(request, 'oth/time_limit.html',
    #                   {'hours': int(hour), 'minutes': int(minutes), 'seconds': int(seconds)})
    question = models.Question.objects.get(pk=kwargs['pk'])
    s = sentiment(ans)
    answer, created = models.Answer.objects.update_or_create(user=player, question=question,
                                                             defaults={'answer': ans, 'sentiment': s})
    # answer.image =
    # answer.sentiment =
    # answer.facial_expression =
    if created:
        player.level = player.level + 1
        player.score = player.score + 10
        player.timestamp = datetime.datetime.now()
        question.numuser = question.numuser + 1
        question.save()

    try:
        if player.level < 5:
            random_question = models.Question.objects.filter(module__module__icontains="demo")
        elif player.level < 10:
            random_question = models.Question.objects.filter(module__module__icontains="2")
        elif player.level < 15:
            random_question = models.Question.objects.filter(module__module__icontains="3")
        elif player.level < 20:
            random_question = models.Question.objects.filter(module__module__icontains="4")
        elif player.level < 25:
            random_question = models.Question.objects.filter(module__module__icontains="5")
        elif player.level < 30:
            random_question = models.Question.objects.filter(module__module__icontains="6")
        elif player.level < 35:
            random_question = models.Question.objects.filter(module__module__icontains="7")
        else:
            player.random_number = 100
            player.save()

            return redirect('oth:finish')

        random_number = random_question[random.randrange(0, random_question.count())].id
        while models.Answer.objects.filter(user=player, question_id=random_number).exists():
            random_number = random_question[random.randrange(0, random_question.count())].id
            # print(random_number)

        player.random_number = random_number
        # if models.Answer.objects.filter
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
        return redirect('oth:index')

    except ValueError:
        return redirect('oth:finish')

    # index(request)
    # try:
    #     level = models..objects.get(leve=player.level)
    #     # return render(request, 'finish.html')
    # except:
    #     return render(request, 'oth/finish.html')
    # global last
    # if player.level > last:
    #     return render(request, 'oth/win.html', {'player': player})
    # return render(request, 'oth/stay_tuned.html', {'player': player})
    # elif ans == "":
    #     pass
    #


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
    return render(request, 'oth/rules.html')


def finish(request):
    return render(request, 'oth/finish2.html')


def stay_tuned(request):
    return render(request, 'oth/stay_tuned.html')


def not_happy(request, **kwargs):
    player = models.Player.objects.get(user_id=request.user.pk)

    return render(request, 'oth/not_happy.html', {'player_emotion': player.player_emotion})


def gen(camera, player):
    while True:
        frame, emotion = camera.get_frame()
        # print(emotion, player)
        player_object = models.Player.objects.get(user_id=player)
        if emotion is not '' and emotion is not "neutral":
            emotion_save = models.Emotion.objects.create(user=player_object, emotion=emotion,
                                                         timestamp=datetime.datetime.now())
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


def video_feed(request):
    return StreamingHttpResponse(gen(VideoCamera(), request.user.pk),
                                 content_type='multipart/x-mixed-replace; boundary=frame')
