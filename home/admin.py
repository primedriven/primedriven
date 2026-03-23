from django.contrib import admin
from .models import EntryLIST, Giveaway

admin.site.register(EntryLIST)


from django.contrib import admin
from .models import Giveaway


@admin.register(Giveaway)
class GiveawayAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "status",
        "draw_time",
        "winner_number_1",
        "winner_number_2",
        "winners_revealed",
        "updated_at",
    )
    list_filter = ("status", "winners_revealed")
    search_fields = ("title", "winner_number_1", "winner_number_2")
