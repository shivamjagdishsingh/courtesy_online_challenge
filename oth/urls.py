from django.urls import path

from oth import views

app_name = 'oth'
urlpatterns = [
    # path('', views.index, name='index'),
    path('', views.index, name='index'),

]
