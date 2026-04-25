from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Player, Team

from django.shortcuts import render, redirect

from django.shortcuts import redirect
from django.shortcuts import render
import random

# 🏠 HOME
def home(request):
    return render(request, 'home.html')
from django.shortcuts import render
import random


# 🔥 AUCTION PAGE (CURRENT PLAYER)
def auction_page(request):

    # 🔥 CURRENT PLAYER (SAFE FETCH)
    player = Player.objects.filter(
        is_sold=False,
        is_unsold=False
    ).order_by('id').first()

    # 🔥 ALL TEAMS
    teams = list(Team.objects.all())

    # 🔥 RANDOM 2 TEAMS FOR LOGO (safe)
    random_teams = []
    if len(teams) >= 2:
        random_teams = random.sample(teams, 2)
    else:
        random_teams = teams

    return render(request, 'auction.html', {
        'player': player,
        'teams': random_teams
    })

    # 🔥 RESET BUTTON LOGIC
    if request.GET.get("reset") == "1":

        if player:
            player.current_bid = 0
            player.team = None
            player.is_retained = False
            player.is_sold = False
            player.save()

        return redirect('/auction/')

from django.shortcuts import render
from .models import Player, Team
import random


def auction_page(request):

    # 🔥 CURRENT PLAYER
    player = Player.objects.filter(
        is_sold=False,
        is_unsold=False
    ).order_by('id').first()

    # 🔥 ALL TEAMS
    teams = list(Team.objects.all())

    # 🔥 RANDOM TEAMS (for header / timer logos)
    random_teams = random.sample(teams, min(len(teams), 2)) if teams else []

    # 🔥 MAIN LOGO TEAM (first team fallback)
    main_team = teams[0] if teams else None

    # 🔥 AUCTION STATUS
    auction_finished = False if player else True

    return render(request, 'auction.html', {
        'player': player,
        'teams': teams,                 # buttons ke liye
        'random_teams': random_teams,   # timer logos ke liye
        'team': main_team,              # header logo ke liye
        'auction_finished': auction_finished
    })

# 🔥 PLACE BID (AUTO SPIN VERSION)
def place_bid(request, player_id):
    player = get_object_or_404(Player, id=player_id)

    if request.method == 'POST':

        if player.is_sold:
            return JsonResponse({"error": "Player already sold"}, status=400)

        team_id = request.POST.get('team_id')
        bid_amount = request.POST.get('bid')

        if not team_id or not bid_amount:
            return JsonResponse({"error": "Invalid data"}, status=400)

        try:
            bid_amount = int(bid_amount)
        except:
            return JsonResponse({"error": "Invalid bid format"}, status=400)

        team = get_object_or_404(Team, id=team_id)

        current_bid = player.current_bid or 0

        # ===============================
        # 🔥 BID VALIDATION (IMPORTANT)
        # ===============================

        # ❌ block lower bids
        if bid_amount < current_bid:
            return JsonResponse({"success": False, "error": "Lower bid not allowed"})

        # ❌ block equal bids EXCEPT 3500
        if bid_amount == current_bid and bid_amount != 3500:
            return JsonResponse({"success": False, "error": "Same bid not allowed"})

        # 💰 purse check (optional for 3500 case)
        if team.purse < bid_amount:
            return JsonResponse({"success": False, "error": "Not enough balance"})

        # ===============================
        # ✅ UPDATE PLAYER
        # ===============================
        player.current_bid = bid_amount

        # ⚠️ IMPORTANT:
        # 👉 team only update when < 3500
        # 👉 3500 pe multiple teams allowed → team fix mat karo
        if bid_amount < 3500:
            player.team = team

        player.save()

        return JsonResponse({
            "success": True,
            "team": team.name,
            "bid": bid_amount
        })

    return JsonResponse({"error": "Invalid request"}, status=400)



from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.db import transaction
from .models import Player, Team

# 🔥 SELL PLAYER (FINAL FIXED)
@transaction.atomic
def sell_player(request, player_id):
    player = get_object_or_404(Player, id=player_id)

    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    # ❌ Already sold check
    if player.is_sold:
        return JsonResponse({"error": "Player already sold"}, status=400)

    team_id = request.POST.get("team_id")
    bid = request.POST.get("bid")

    if not team_id:
        return JsonResponse({"error": "No team selected"}, status=400)

    team = get_object_or_404(Team, id=team_id)

    # 💰 FINAL PRICE LOGIC
    if bid:
        try:
            final_price = int(bid)
        except ValueError:
            return JsonResponse({"error": "Invalid bid"}, status=400)
    else:
        final_price = player.current_bid if player.current_bid > 0 else player.base_price

    # ❌ Purse check
    if team.purse < final_price:
        return JsonResponse({"error": "Not enough purse"}, status=400)

    # ===============================
    # 🔥 MAIN FIX (VERY IMPORTANT)
    # ===============================
    player.is_sold = True
    player.is_unsold = False      # ✅ UNSOLD reset (core bug fix)
    player.team = team
    player.sold_price = final_price
    player.current_bid = final_price

    # optional: round reset (clean state)
    player.round_number = 1

    player.save()

    # 💰 CUT TEAM PURSE
    team.purse -= final_price
    team.save()

    # 🎯 RESPONSE (ANIMATION USE)
    return JsonResponse({
        "success": True,
        "player_name": player.name,
        "team_name": team.name,
        "player_image": player.image_url,
        "amount": final_price
    })

# ❌ MARK UNSOLD (OPTIONAL)
def mark_unsold(request, player_id):
    player = get_object_or_404(Player, id=player_id)

    player.is_unsold = True
    player.save()

    return JsonResponse({"success": True})


# 🏆 TEAMS LIST
def teams_view(request):
    teams = Team.objects.all()

    data = []

    for team in teams:
        players = Player.objects.filter(team=team, is_sold=True)

        data.append({
            'team': team,
            'players': players
        })

    return render(request, 'teams.html', {'data': data})


# 📄 TEAM DETAIL
def team_detail(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    players = Player.objects.filter(team=team, is_sold=True)

    return render(request, 'team_detail.html', {
        'team': team,
        'players': players
    })


# 📋 ALL PLAYERS
def all_players(request):
    players = Player.objects.all().order_by('player_id')

    return render(request, 'all_players.html', {
        'players': players
    })
def retain_player(request, player_id):
    player = get_object_or_404(Player, id=player_id)

    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

    team_id = request.POST.get("team_id")

    if not team_id:
        return JsonResponse({"success": False, "error": "No team selected"})

    try:
        team = Team.objects.get(id=team_id)
    except Team.DoesNotExist:
        return JsonResponse({"success": False, "error": "Invalid team"})

    # 🔥 MAIN LOGIC (MODEL HANDLE KAREGA SAB)
    success, message = player.apply_retain(team)

    if not success:
        return JsonResponse({
            "success": False,
            "error": message
        })

    # 🔥 FRESH DATA (important for UI sync)
    team.refresh_from_db()
    player.refresh_from_db()

    return JsonResponse({
        "success": True,
        "message": message,

        "player_name": player.name,
        "team_name": team.name,
        "player_image": player.image_url,

        "retain_count": team.retain_count,   # 🔥 UI update ke liye
        "purse": team.purse                  # 🔥 optional (live update)
    })

def reset_full_auction(request):

    # 🔥 ALL PLAYERS RESET
    Player.objects.update(
        current_bid=0,
        sold_price=0,
        team=None,
        is_sold=False,
        is_retained=False,
        is_unsold=False
    )

    # 🔥 ALL TEAMS RESET
    Team.objects.update(
        purse=35000,
        retain_count=0
    )

    return redirect('/auction/')

from django.contrib.auth.models import User
from django.http import HttpResponse

def temp_login(request):
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@gmail.com', 'admin123')
        return HttpResponse("Admin created successfully ✅")
    return HttpResponse("Admin already exists 👍")


from django.http import JsonResponse
from .models import Player
import random


# ===============================
# ❌ UNSOLD PLAYER
# ===============================
from django.http import JsonResponse
from .models import Player

def unsold_player(request, player_id):

    if request.method == "POST":
        try:
            player = Player.objects.get(id=player_id)

            # 🔥 UNSOLD LOGIC
            player.is_unsold = True
            player.is_sold = False
            player.is_retained = False

            player.current_bid = 0
            player.sold_price = None
            player.team = None

            # 🔁 MOVE TO RE-AUCTION ROUND
            player.round_number = 2

            player.save()

            return JsonResponse({
                "success": True,
                "message": f"{player.name} moved to re-auction"
            })

        except Player.DoesNotExist:
            return JsonResponse({
                "success": False,
                "error": "Player not found"
            })

    return JsonResponse({
        "success": False,
        "error": "Invalid request"
    })

# ===============================
# 🔥 NEXT PLAYER (RANDOM)
# ===============================
def next_player(request):

    # ===============================
    # 🔥 ROUND 1 (Normal Players)
    # ===============================
    player = Player.objects.filter(
        is_sold=False,
        is_unsold=False,
        round_number=1
    ).order_by('id').first()

    # ===============================
    # 🔥 ROUND 2 (UNSOLD Players)
    # ===============================
    if not player:
        player = Player.objects.filter(
            is_sold=False,
            is_unsold=True,
            round_number=2
        ).order_by('id').first()

    # ===============================
    # 🏁 FINISHED
    # ===============================
    if not player:
        return JsonResponse({
            "finished": True
        })

    return JsonResponse({
        "finished": False,
        "id": player.id,
        "player_code": player.player_id,
        "name": player.name,
        "role": player.role,
        "base_price": player.base_price,
        "current_bid": player.current_bid,
        "image": player.image_url
    })