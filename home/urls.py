from . import views
from django.urls import path

urlpatterns = [
    path("", views.home_view, name="home"),
    path("rules-and-conditions/", views.rules_page, name="rules"),
    path("live-draw/", views.livedraw_page, name="livedraw"),
]
