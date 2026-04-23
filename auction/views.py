from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Player, Team

from django.shortcuts import render, redirect

from django.shortcuts import redirect


# 🏠 HOME
def home(request):
    return render(request, 'home.html')

# 🔥 AUCTION PAGE (CURRENT PLAYER)
def auction_page(request):

    # 🔥 CURRENT PLAYER (SAFE FETCH)
    player = Player.objects.filter(
        is_sold=False,
        is_unsold=False
    ).order_by('id').first()

    # 🔥 RESET BUTTON LOGIC
    if request.GET.get("reset") == "1":

        if player:
            player.current_bid = 0
            player.team = None              # ✅ REMOVE TEAM
            player.is_retained = False
            player.is_sold = False
            player.save()

        # 🔥 IMPORTANT → redirect to clean URL
        return redirect('/auction/')

    # 🔥 TEAMS (AFTER RESET)
    teams = Team.objects.all()

    return render(request, 'auction.html', {
        'player': player,
        'teams': teams
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



# 🔥 SELL PLAYER (FINAL + ANIMATION READY)
def sell_player(request, player_id):
    player = get_object_or_404(Player, id=player_id)

    if request.method == "POST":

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
            except:
                return JsonResponse({"error": "Invalid bid"}, status=400)
        else:
            # 👉 Wheel / auto case
            final_price = player.current_bid if player.current_bid > 0 else player.base_price

        # ❌ Purse check
        if team.purse < final_price:
            return JsonResponse({"error": "Not enough purse"}, status=400)

        # ✅ UPDATE PLAYER
        player.current_bid = final_price
        player.sold_price = final_price
        player.is_sold = True
        player.team = team
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

    return JsonResponse({"error": "Invalid request"}, status=400)


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