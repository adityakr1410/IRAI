
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
    path('managers/', manager_list_view, name='manager_list'),
    path('manager/<int:manager_id>/', manager_detail_view, name='manager_detail'),
    path("give-money-to-manager/", give_money_to_manager_view, name="give_money_to_manager"),
    path('add-money/', add_money_to_manager, name='add_money'),
    path('add-expense/', add_miscellaneous_expense, name='add_miscellaneous_expense'),
    path('transactions/', master_transaction_view, name='master_transaction'),
    
]
