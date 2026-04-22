from django.contrib import admin
from .models import Player, Team


# 🔥 Player Admin Customize
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('player_id', 'name', 'role', 'base_price', 'current_bid', 'team', 'is_sold')
    search_fields = ('player_id', 'name', 'role')
    list_filter = ('role', 'team', 'is_sold')
    ordering = ('player_id',)


# 🔥 Team Admin Customize
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'purse')
    search_fields = ('name',)


# ✅ Register
admin.site.register(Player, PlayerAdmin)
admin.site.register(Team, TeamAdmin)