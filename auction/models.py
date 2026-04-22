from django.db import models


class Team(models.Model):
    name = models.CharField(max_length=100)
    purse = models.IntegerField()

    # ✅ Team logo
    logo = models.ImageField(upload_to='teams/', null=True, blank=True)

    def __str__(self):
        return self.name


class Player(models.Model):
    # ✅ Manual Player ID
    player_id = models.CharField(max_length=20, unique=True)

    name = models.CharField(max_length=100)
    role = models.CharField(max_length=50)

    # 💰 Pricing
    base_price = models.IntegerField()
    current_bid = models.IntegerField(default=0)
    sold_price = models.IntegerField(null=True, blank=True)

    # ✅ Team relation
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True)

    # 🔥 Status
    is_sold = models.BooleanField(default=False)
    is_unsold = models.BooleanField(default=False)

    # 🆕 🔥 RETAIN SYSTEM
    is_retained = models.BooleanField(default=False)

    # 🖼️ Player image
    image = models.ImageField(upload_to='players/', null=True, blank=True)

    # 🕒 Tracking
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.player_id} - {self.name}"

    # ✅ Safe image (frontend crash avoid karega)
    @property
    def image_url(self):
        if self.image:
            return self.image.url
        return "/static/images/default.png"

    # 🔥 AUTO RETAIN APPLY (OPTIONAL POWER FEATURE)
    def apply_retain(self, team, price=3500):
        self.is_retained = True
        self.is_sold = True
        self.team = team
        self.current_bid = price
        self.sold_price = price
        self.save()

        # 💰 purse cut
        team.purse -= price
        team.save()