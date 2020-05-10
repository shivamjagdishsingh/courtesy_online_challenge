from django.urls import path

from oth import views

app_name = 'oth'
urlpatterns = [
    # path('', views.index, name='index'),
    path('', views.index, name='index'),
    # path(r'^display/$', views.display, name='display'),
    path('answer/<int:pk>', views.answer, name='answer'),
    path('lboard/', views.lboard, name='lboard'),
    path('rules/', views.rules, name='rules'),
    # path(r'^notif/$', views.getNotif, name='getNotif'),

]
