from . import views
from django.urls import path

urlpatterns = [
    path("", views.dashboard, name="admindashboard"),
    path("send-message/", views.accept_entry_mail, name="accept_entry_mail"),
    path("confrim-latter/", views.sweep_stakes_confim, name="sweep_stakes_confim"),
]
