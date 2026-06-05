import json
import os
import requests
from decimal import Decimal
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from django.http import HttpResponse
from baseapp.utils import send_html_email
from manager.decorator import manager_required
from home.forms import JoinListForm, JoinMemberForm
from home.models import EntryLIST
from .models import Giveaway
from manager.models import ProgressBar

FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")


ONESIGNAL_APP_ID = os.getenv("ONESIGNAL_APP_ID")
ONESIGNAL_API_KEY = os.getenv("ONESIGNAL_API_KEY")


def get_helper_model():
    helper = {
        "percent": 0,
        "winning_number": "PD-0401-0389",
        "draw_date": "00-00-2026",
        "draw_time": "7:30PM",
    }
    helper_mod = ProgressBar.objects.first()
    if helper_mod:
        helper = {
            "percent": helper_mod.percent,
            "winning_number": helper_mod.winning_number,
            "draw_date": helper_mod.draw_date,
            "draw_time": helper_mod.draw_time,
        }

    return helper


def get_active_giveaway():
    """
    Picks the most recent giveaway.
    """
    return Giveaway.objects.order_by("-created_at").first()


def get_entry_percent():
    progressbar = ProgressBar.objects.first()
    if progressbar:
        return progressbar.percent
    return Decimal("100")


class GiveawayView(View):
    template_name = "index.html"

    def get_context(self):
        giveaway = get_active_giveaway()
        percent = get_entry_percent()
        return giveaway, percent

    def get(self, request):
        giveaway, percent = self.get_context()
        number_count = percent / 100 * 500
        helper = ProgressBar.objects.first()
        if not helper:
            return render(
                request,
                "livepick.html",
                {
                    "giveaway": giveaway,
                    "state": "closed",
                    "preview_numbers": [],
                    "draw_time_iso": "",
                },
            )

        if not giveaway or giveaway.status == "closed":
            return render(
                request,
                "livepick.html",
                {
                    "giveaway": giveaway,
                    "state": "closed",
                    "preview_numbers": [],
                    "draw_time_iso": "",
                },
            )

        draw_time = giveaway.draw_time.isoformat()
        return render(
            request,
            self.template_name,
            {
                "form": JoinListForm(),
                "percent": percent,
                "draw_time": draw_time,
                "number_count": number_count,
                "draw_date": helper.draw_date,
            },
        )

    def post(self, request):

        giveaway, _ = self.get_context()
        if not giveaway or giveaway.status == "closed":
            return JsonResponse(
                {"success": False, "message": "No active giveaway."}, status=400
            )

        step = request.POST.get("step")

        # ── step 1: save core details, return id ──
        if step == "1":
            form = JoinListForm(request.POST)
            print(form)

            if form.is_valid():

                subject = "Your Entry Is Approved — Prime EV"
                reciever_email = request.POST.get("email")
                template = "mail/entry_approved.html"
                helper = get_helper_model()

                context = {
                    "name": request.POST.get("full_name"),
                    "entry_num": helper.get("winning_number"),
                    "draw_date": helper.get("draw_date"),
                    "draw_time": helper.get("draw_time"),
                    "unsubscribe_url": "https://primedriven.live/",
                }
                mail = send_html_email(
                    subject=subject,
                    receiver_email=reciever_email,
                    template_name=template,
                    context=context,
                    from_email=FROM_EMAIL,
                )

                if mail["success"] == False:
                    return JsonResponse(
                        {
                            "success": False,
                            "email_success": mail.get("success"),
                        }
                    )

                entry = form.save()

                return JsonResponse(
                    {
                        "success": True,
                        "entry_id": entry.id,
                        "email_success": mail.get("success"),
                    }
                )
            return JsonResponse({"success": False, "errors": form.errors}, status=400)

        # ── step 2: update contact preference on existing entry ──
        if step == "2":
            entry_id = request.POST.get("entry_id")
            try:
                entry = EntryLIST.objects.get(id=entry_id)
            except EntryLIST.DoesNotExist:
                return JsonResponse(
                    {"success": False, "message": "Entry not found."}, status=404
                )

            entry.contact_preference = request.POST.get("contact_preference", "")
            
            entry.save()
            return JsonResponse({"success": True})

        return JsonResponse({"success": False, "message": "Invalid step."}, status=400)


class HomeView(GiveawayView):
    template_name = "index.html"


class HomeAUView(GiveawayView):
    template_name = "index-au.html"


def past_winners_view(request):
    return render(request, "pastwinners.html")


def rules_page(request):
    return render(request, "regulations.html")


def livepick_view(request):
    giveaway = get_active_giveaway()

    if not giveaway:
        context = {
            "giveaway": None,
            "state": "closed",
            "preview_numbers": [],
            "draw_time_iso": "",
        }
        return render(request, "livepick.html", context)

    state = giveaway.current_frontend_state()

    preview_numbers = (
        giveaway.preview_numbers
        if giveaway.preview_numbers
        else [
            "PD-26-0401-104",
            "PD-26-0401-078",
            "PD-26-0401-051",
            "PD-26-0401-015",
            "PD-26-0401-055",
            "PD-26-0401-012",
            "PD-26-0401-111",
            "PD-26-0401-073",
        ]
    )

    context = {
        "giveaway": giveaway,
        "state": state,
        "preview_numbers": preview_numbers,
        "draw_time_iso": giveaway.draw_time.isoformat() if giveaway.draw_time else "",
    }
    return render(request, "livepick.html", context)


def giveaway_reveal_api(request):
    giveaway = get_active_giveaway()

    if not giveaway:
        return JsonResponse({"error": "No giveaway found"}, status=404)

    now = timezone.now()

    if giveaway.status == "closed":
        return JsonResponse({"error": "Giveaway is closed"}, status=400)

    if not giveaway.draw_time:
        return JsonResponse({"error": "Draw time is not set"}, status=400)

    if now < giveaway.draw_time:
        return JsonResponse({"error": "Draw has not started yet"}, status=400)

    if not giveaway.winner_number_1 or not giveaway.winner_number_2:
        return JsonResponse({"error": "Winning numbers are not set"}, status=400)

    # mark revealed once draw is requested after draw time
    if not giveaway.winners_revealed:
        giveaway.winners_revealed = True
        giveaway.status = "completed"
        giveaway.save(update_fields=["winners_revealed", "status", "updated_at"])

    return JsonResponse(
        {
            "success": True,
            "winners": [
                str(giveaway.winner_number_1).zfill(3),
                str(giveaway.winner_number_2).zfill(3),
            ],
        }
    )


def giveaway_status_api(request):
    """
    Optional polling endpoint in case the page stays open for a long time.
    """
    giveaway = get_active_giveaway()

    if not giveaway:
        return JsonResponse({"exists": False, "state": "closed"})

    return JsonResponse(
        {
            "exists": True,
            "state": giveaway.current_frontend_state(),
            "draw_time": giveaway.draw_time.isoformat() if giveaway.draw_time else "",
            "winners_revealed": giveaway.winners_revealed,
        }
    )


@manager_required
def download_entries_txt(request):
    entries = EntryLIST.objects.all().order_by("id")

    # --- Build table ---
    col_widths = {"id": 6, "name": 25, "number": 15, "email": 30}

    def row(id, name, number, email):
        return (
            f"{str(id):<{col_widths['id']}}"
            f"{str(name):<{col_widths['name']}}"
            f"{str(number):<{col_widths['number']}}"
            f"{str(email):<{col_widths['email']}}"
        )

    separator = "-" * sum(col_widths.values())

    lines = [
        "ENTRY FORM RECORDS",
        f"Total entries: {entries.count()}",
        "",
        separator,
        row("ID", "Name", "Number", "Email"),
        separator,
    ]

    for entry in entries:
        lines.append(row(entry.id, entry.full_name, entry.phone_number, entry.email))

    lines.append(separator)

    content = "\n".join(lines)

    response = HttpResponse(content, content_type="text/plain")
    response["Content-Disposition"] = 'attachment; filename="entries.txt"'
    return response


def members_page(request):
    if request.method == "POST":

        form = JoinMemberForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return JsonResponse(
                {
                    "success": True,
                    "message": "Uploaded successfully",
                    "name": request.POST.get("name", ""),
                    "email": request.POST.get("email", ""),
                    "entry": request.POST.get("entry", ""),
                }
            )

        return JsonResponse({"success": False, "errors": form.errors}, status=400)
    else:
        form = JoinMemberForm()
    return render(request, "member.html")
