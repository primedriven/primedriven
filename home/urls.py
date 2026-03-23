from . import views
from django.urls import path

urlpatterns = [
    path("", views.home_view, name="home"),
    path("rules-and-conditions/", views.rules_page, name="rules"),
    # path("live-draw/", views.livedraw_page, name="livedraw"),
    path("live-draw/", views.livepick_view, name="livepick"),
    path("api/giveaway/reveal/", views.giveaway_reveal_api, name="giveaway_reveal_api"),
    path("api/giveaway/status/", views.giveaway_status_api, name="giveaway_status_api"),
]
