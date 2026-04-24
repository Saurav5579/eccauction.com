from django.db import models, transaction
from cloudinary.models import CloudinaryField   # 👈 IMPORTANT


# =========================
# TEAM MODEL
# =========================
class Team(models.Model):
    name = models.CharField(max_length=100)

    # 💰 DEFAULT PURSE
    purse = models.IntegerField(default=35000)

    # 🔒 RETAIN LIMIT TRACK
    retain_count = models.IntegerField(default=0)

    # 🖼️ LOGO (Cloudinary)
    logo = CloudinaryField('image', null=True, blank=True)

    def __str__(self):
        return self.name


# =========================
# PLAYER MODEL
# =========================
class Player(models.Model):
    player_id = models.CharField(max_length=20, unique=True)

    name = models.CharField(max_length=100)
    role = models.CharField(max_length=50)

    # 💰 PRICING
    base_price = models.IntegerField()
    current_bid = models.IntegerField(default=0)
    sold_price = models.IntegerField(null=True, blank=True)

    # 🏏 TEAM
    team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # 🔥 STATUS
    is_sold = models.BooleanField(default=False)
    is_unsold = models.BooleanField(default=False)
    is_retained = models.BooleanField(default=False)

    # 🖼️ IMAGE (Cloudinary)
    image = CloudinaryField('image', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.player_id} - {self.name}"

    # ✅ SAFE IMAGE URL
    @property
    def image_url(self):
        if self.image:
            return self.image.url
        return "https://res.cloudinary.com/demo/image/upload/sample.jpg"  # fallback

    # ======================================
    # 🔒 RETAIN FUNCTION
    # ======================================
    def apply_retain(self, team, price=3500):

        with transaction.atomic():

            self.refresh_from_db()
            team.refresh_from_db()

            if self.is_sold or self.is_retained:
                return False, "Player already sold"

            if team.retain_count >= 3:
                return False, "Retain limit reached"

            if team.purse < price:
                return False, "Not enough purse"

            # ✅ APPLY
            self.is_retained = True
            self.is_sold = True
            self.team = team
            self.current_bid = price
            self.sold_price = price
            self.save()

            # 💰 TEAM UPDATE
            team.purse -= price
            team.retain_count += 1
            team.save()

            return True, "Retained successfully"

    # ======================================
    # 🔄 RESET PLAYER
    # ======================================
    def reset_player(self):

        self.current_bid = 0
        self.sold_price = None
        self.team = None

        self.is_sold = False
        self.is_unsold = False
        self.is_retained = False

        self.save()