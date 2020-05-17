from django.urls import path

from oth import views

app_name = 'oth'
urlpatterns = [
    path('', views.index, name='index'),
    path('answer/<int:pk>', views.answer, name='answer'),
    path('lboard/', views.lboard, name='lboard'),
    path('rules/', views.rules, name='rules'),
    path('finish/', views.finish, name='finish'),
    path('video_feed', views.video_feed, name='video_feed'),

    # path(r'^notif/$', views.getNotif, name='getNotif'),

]
