from django.contrib import admin
from .models import EntryLIST, Giveaway, Member


from django.urls import path, reverse
from django.utils.html import format_html
from .views import download_entries_txt


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


admin.site.register(EntryLIST)
admin.site.register(Member)
