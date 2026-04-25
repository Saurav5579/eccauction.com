from django.urls import path
from . import views

# MEDIA FILES
from django.conf import settings
from django.conf.urls.static import static
from auction.views import temp_login

urlpatterns = [
    # 🏠 HOME
    path('', views.home, name='home'),

    # 🎯 AUCTION
    path('auction/', views.auction_page, name='auction_page'),

    # 💰 BID (AJAX)
    path('place-bid/<int:player_id>/', views.place_bid, name='place_bid'),

    # 🔥 SELL PLAYER (IMPORTANT)
    path('sell-player/<int:player_id>/', views.sell_player, name='sell_player'),

    # ❌ UNSOLD (optional)
    path('unsold/<int:player_id>/', views.mark_unsold, name='mark_unsold'),

    # 🏆 TEAMS
    path('teams/', views.teams_view, name='teams_view'),

    # 📄 TEAM DETAIL
    path('team/<int:team_id>/', views.team_detail, name='team_detail'),

    # 📋 ALL PLAYERS
    path('players/', views.all_players, name='all_players'),
    
     # 🔥 PLAYERS
    path('players/', views.all_players, name='all_players'),

    # 🔒 RETAIN
    path('retain-player/<int:player_id>/', views.retain_player, name='retain_player'),

    # 🔄 RESET AUCTION
    path('reset-auction/', views.reset_full_auction, name='reset_auction'),

    # 🔐 TEMP LOGIN
    path('temp-login/', temp_login, name='temp_login'),

    # ❌ UNSOLD
    path('unsold_player/<int:player_id>/', views.unsold_player, name='unsold_player'),

    # 🔥 NEXT PLAYER
    path('next-player/', views.next_player, name='next_player'),

]



# 📁 MEDIA FILES (IMAGES FIX)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)