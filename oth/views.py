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
from django.contrib.humanize.templatetags.humanize import ordinal

# Create your views here.

m_level = 1
f_user = ""
last = 100


def get_emotion(player):
    """
    get_emotions function gets the MAX emotions count of user and saves automatically,
    when user answers the question
    """

    oneday = datetime.datetime.now() - datetime.timedelta(days=1)
    emotion_shivam = models.Emotion.objects.filter(user=player, timestamp__gt=oneday)
    if emotion_shivam:
        emotion_list = [emotion.emotion for emotion in emotion_shivam]
        bb = dict(zip(emotion_list, [emotion_list.count(i) for i in emotion_list]))
        final_emotion = max(bb, key=bb.get)
        player.player_emotion = final_emotion
        # player.save()


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


def save_answer(ans, question, player):
    """
    This function saves answer given by user.
    """
    s = sentiment(ans)
    answer, created = models.Answer.objects.update_or_create(user=player, question=question,
                                                             defaults={'answer': ans, 'sentiment': s})
    player.video_viewed = 0
    # player.save()
    # answer.image =
    # answer.facial_expression =
    if created:
        player.score = player.score + 10
        player.timestamp = datetime.datetime.now()
        question.numuser = question.numuser + 1
        # player.save()
        # question.save()


def one_day_limitation(request, player):
    """
    one_day_limitation restricts user to answer any question if he has already answered in time range of 24 hours
    """

    if (datetime.datetime.now(datetime.timezone.utc) - player.timestamp).days < 1:
        seconds = 86400 - (datetime.datetime.now(datetime.timezone.utc) - player.timestamp).total_seconds()
        seconds = seconds % (24 * 3600)
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60

    return render(request, 'oth/time_limit.html',
                  {'hours': int(hour), 'minutes': int(minutes), 'seconds': int(seconds)})


def user_question_assignment(player):
    if player.score == 50:
        if player.level == 7:
            player.base_module = models.Module.objects.get(module_number=2)
        elif player.level == 8:
            player.base_module = models.Module.objects.get(module_number=3)
        elif player.level == 9:
            player.base_module = models.Module.objects.get(module_number=4)
        elif player.level == 10:
            player.base_module = models.Module.objects.get(module_number=5)
        elif player.level == 11:
            player.base_module = models.Module.objects.get(module_number=6)
        # player.save()

    if player.score < 50:
        random_question = models.Question.objects.filter(module__module_number="0")
    elif player.score >= 50:
        questions_answered = (player.score - 50) / 10
        if not questions_answered:
            modules_solved = 0
        else:
            modules_solved = int(questions_answered / 5)
        final_module = player.base_module.module_number + modules_solved
        if final_module == 7 and questions_answered % 5 == 0:
            player.random_number = 100
            player.save()
            return redirect('oth:finish')
        else:
            random_question = models.Question.objects.filter(module__module_number=final_module)
        # elif final_module == 2:
        #     random_question = models.Question.objects.filter(module__module_number="2")
        # elif final_module == 3:
        #     random_question = models.Question.objects.filter(module__module_number="3")
        # elif final_module == 4:
        #     random_question = models.Question.objects.filter(module__module_number="4")
        # elif final_module == 5:
        #     random_question = models.Question.objects.filter(module__module_number="5")
        # elif final_module == 6:
        #     random_question = models.Question.objects.filter(module__module_number="6")
        # elif final_module == 7:
        #     random_question = models.Question.objects.filter(module__module_number="7")

    random_number = random_question[random.randrange(0, random_question.count())].id
    while models.Answer.objects.filter(user=player, question_id=random_number).exists():
        random_number = random_question[random.randrange(0, random_question.count())].id

    player.random_number = random_number

    global m_level
    global f_user
    if m_level < player.level:
        m_level = player.level
        f_user = player.name

    # player.save()


@login_required
def index(request):
    user = request.user
    if user.is_authenticated:
        player = models.Player.objects.get(user_id=request.user.pk)
        get_emotion(player)
        if player.random_number == 100:
            return redirect('oth:finish')
        time_delta = (datetime.datetime.now(datetime.timezone.utc) - player.timestamp)

        # one_day_limitation(request, player)

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
    player = models.Player.objects.get(user_id=request.user.pk)

    """
    The two line code below redirects User to not happy page, if player's emotion is not happy.
    """
    # if not 'happy'.__eq__(player.player_emotion):
    #     return redirect('oth:not_happy')

    # one_day_limitation(request, player)

    question = models.Question.objects.get(pk=kwargs['pk'])

    get_emotion(player)

    if request.method == 'POST':
        if request.POST.get('option'):
            """
            If user answers an MCQ question, this condition is selected.
            In this case, User's level increases by the option's level of the question he selects.
            """

            ans = request.POST.get('option')

            if ans == "option1":
                player.level += question.option1_level_score
                ans = question.option1
            elif ans == "option2":
                player.level += question.option2_level_score
                ans = question.option2
            # player.save()

            save_answer(ans, question, player)


        elif request.POST.get('answer'):
            """
            If user writes an answer to a Non-MCQ question, this condition is selected.
            In this case, user's level increases by 1.
            """

            ans = request.POST.get('answer')
            player.level += 1
            # player.save()

            save_answer(ans, question, player)

    try:

        user_question_assignment(player)
        player.save()
        question.save()
        return redirect('oth:index')

    except ValueError:
        return redirect('oth:finish')

    # global last
    # if player.level > last:
    #     return render(request, 'oth/win.html', {'player': player})


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


def view_video(request, **kwargs):
    player = models.Player.objects.get(user_id=request.user.pk)
    video_view_count = player.video_viewed
    counts_remaining = 3 - player.video_viewed
    question = models.Question.objects.get(pk=kwargs['pk'])

    if video_view_count < 3:
        player.video_viewed += 1
        player.save()
        return render(request, 'oth/video.html',
                      {'question': question, 'player': player, 'counts_remaining': counts_remaining})

    return render(request, 'oth/video.html', {'player': player})


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
