from django.db import models
from django.utils import timezone


class EntryLIST(models.Model):
    email = models.EmailField(
        verbose_name="email", max_length=60, blank=True, null=True
    )
    full_name = models.CharField(max_length=200, blank=True, null=True)
    phone_number = models.CharField(max_length=11, blank=True, null=True)
    is_accepted = models.BooleanField(default=False)

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
