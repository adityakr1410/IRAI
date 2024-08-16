
from django.urls import path
from .views import *


urlpatterns = [
    path("",home,name="home"),
    path("payment_summary/",payment_summary_view,name="payment_summary"),
    path('fisherman/<int:fisherman_id>/unpaid-catches/', unpaid_catches_view, name='unpaid_catches'),
    path('log_catch/', log_catch, name='log_catch'),
    path('fisherman/<int:fisherman_id>/give-advance/', give_advance_view, name='give_advance'),
    path('log_catch_royalty/', log_catch_royalty, name='register_catch_royalty'),
    path('fishermanRoyalty-summary/', fishermanRoyalty_summary, name='fishermanRoyalty_summary'),
    path('fishermanRoyalty-detail/<int:pk>/', fishermanRoyalty_detail, name='fishermanRoyalty_detail'),
]
