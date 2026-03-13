from . import views
from django.urls import path, include

urlpatterns = [
    path("", views.home_view, name="home"),
    path("rules-and-conditions/", views.rules_page, name="rules"),
]
