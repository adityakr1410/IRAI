
from django.urls import path
from .views import *


urlpatterns = [
    path("",home,name="home"),
    path("payment_summary/",payment_summary_view,name="payment_summary"),
    path('fisherman/<int:fisherman_id>/unpaid-catches/', unpaid_catches_view, name='unpaid_catches'),
    path('log_catch/', log_catch, name='log_catch'),
]
