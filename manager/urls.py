from . import views
from home.views import download_entries_txt
from django.urls import path

urlpatterns = [
    path("", views.dashboard, name="admindashboard"),
    path("send-message/", views.accept_entry_mail, name="accept_entry_mail"),
    # path("confrim-latter/", views.sweep_stakes_confim, name="sweep_stakes_confim"),
    # path("send-congrat/", views.send_congrat, name="send_congrat"),
    # path("draw-day-reminder/", views.send_reminder, name="send_reminder"),
    path("email-panel/", views.send_email_panel, name="send_email_panel"),
    path(
        "download-entries/",
        download_entries_txt,
        name="download_entries_txt",
    ),
]
