from django.db import models
from django.utils import timezone
 


class EntryLIST(models.Model):

    full_name = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)

    email = models.EmailField(
        verbose_name="email", max_length=60, blank=True, null=True
    )
    phone = models.CharField(max_length=20, blank=True, null=True)
    contact_preference = models.CharField(max_length=20)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_accepted = models.BooleanField(default=False)
    is_draw_reminded = models.BooleanField(default=False)

    is_congratulations = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name


class Giveaway(models.Model):
    STATUS_CHOICES = [
        ("closed", "Closed"),
        ("open", "Open"),
        ("completed", "Completed"),
    ]

    title = models.CharField(max_length=255, default="Current Giveaway")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="closed")

    signup_start = models.DateTimeField(null=True, blank=True)
    signup_end = models.DateTimeField(null=True, blank=True)
    draw_time = models.DateTimeField(null=True, blank=True)

    winner_number_1 = models.CharField(max_length=20, blank=True, null=True)
    winner_number_2 = models.CharField(max_length=20, blank=True, null=True)

    winners_revealed = models.BooleanField(default=False)

    # optional preview numbers to show on the page
    preview_numbers = models.JSONField(default=list, blank=True)

    banner_closed_text = models.CharField(
        max_length=255,
        default="Giveaway currently closed. Stay updated for the next round.",
    )

    banner_open_text = models.CharField(
        max_length=255, default="Giveaway is live. Winners will be picked soon."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def current_frontend_state(self):
        now = timezone.now()

        if self.status == "closed":
            return "closed"

        if self.winners_revealed or self.status == "completed":
            return "completed"

        if self.draw_time and now < self.draw_time:
            return "open"

        if self.draw_time and now >= self.draw_time:
            return "drawing"

        return "closed"


class Member(models.Model):
    email = models.EmailField(
        verbose_name="email", max_length=60, blank=True, null=True
    )
    full_name = models.CharField(max_length=200, blank=True, null=True)
    entry_number = models.CharField(max_length=200, blank=True, null=True)

    ss = models.ImageField(upload_to="profile_pics/", blank=True, null=True)

    def __str__(self):
        return self.full_name








class PrizeClaim(models.Model):

    STATUS_CHOICES = [
        ("pending",   "Pending Review"),
        ("verified",  "Verified"),
        ("rejected",  "Rejected"),
        ("delivered", "Delivered"),
    ]

    # linked entry number as typed by the claimant
    full_name    = models.CharField(max_length=255)
    entry_number = models.CharField(max_length=50)
    id_type      = models.CharField(max_length=50)
    id_file      = models.FileField(upload_to="prize_claims/ids/")
    status       = models.CharField(
                     max_length=20,
                     choices=STATUS_CHOICES,
                     default="pending"
                   )
    notes        = models.TextField(blank=True)  # admin use only
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-submitted_at"]
        verbose_name      = "Prize Claim"
        verbose_name_plural = "Prize Claims"

    def __str__(self):
        return f"#{self.entry_number} — {self.full_name} ({self.status})"