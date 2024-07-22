
from django.urls import path
from .views import *


urlpatterns = [
    path("",home,name="home"),
    path("catch/",catches,name="catch"),
    path("fisherman/<id>/",fisherMan,name="fisherManID"),
    path("allfisherman/",allFisherman,name="allfisherman"),
]
