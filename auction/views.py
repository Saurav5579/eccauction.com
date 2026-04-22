from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Player, Team


# 🏠 HOME
def home(request):
    return render(request, 'home.html')


# 🔥 AUCTION PAGE (CURRENT PLAYER)
def auction_page(request):
    player = Player.objects.filter(is_sold=False, is_unsold=False).order_by('id').first()
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
# 🔥 RETAIN PLAYER (AUTO)
def retain_player(request, player_id):
    player = get_object_or_404(Player, id=player_id)

    if request.method == "POST":

        if player.is_sold:
            return JsonResponse({"error": "Already sold"}, status=400)

        team_id = request.POST.get("team_id")

        if not team_id:
            return JsonResponse({"error": "No team selected"}, status=400)

        team = get_object_or_404(Team, id=team_id)

        retain_price = 3500

        # ❌ purse check
        if team.purse < retain_price:
            return JsonResponse({"error": "Not enough purse"}, status=400)

        # ✅ UPDATE PLAYER
        player.current_bid = retain_price
        player.sold_price = retain_price
        player.is_sold = True
        player.is_retained = True
        player.team = team
        player.save()

        # 💰 CUT PURSE
        team.purse -= retain_price
        team.save()

        return JsonResponse({
            "success": True,
            "player_name": player.name,
            "team_name": team.name,
            "player_image": player.image_url,
            "amount": retain_price
        })

    return JsonResponse({"error": "Invalid request"}, status=400)