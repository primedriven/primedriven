import json
from decimal import Decimal
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from manager.decorator import manager_required
from home.forms import JoinListForm
from home.models import EntryLIST
from .models import Giveaway
from manager.models import ProgressBar


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


def past_winners_view(request):
    return render(request, "pastwinners.html")


def home_view(request):
    giveaway = get_active_giveaway()
    percent = get_entry_percent()

    # CASE 1: no giveaway at all
    if not giveaway:
        return render(
            request,
            "livepick.html",
            {
                "giveaway": None,
                "state": "closed",
                "preview_numbers": [],
                "draw_time_iso": "",
            },
        )

    # CASE 2: giveaway exists but is closed
    if giveaway.status == "closed":
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

    # CASE 3: active giveaway
    state = giveaway.current_frontend_state()

    if request.method == "POST":
        try:
            data = json.loads(request.body)

            form = JoinListForm(data)

            if form.is_valid():
                form.save()

                return JsonResponse(
                    {
                        "status": "success",
                        "message": "Application received. We'll be in touch soon.",
                    },
                    status=201,
                )

            else:
                # Return form validation errors
                return JsonResponse(
                    {"status": "error", "errors": form.errors.as_json()}, status=400
                )

        except json.JSONDecodeError:
            return JsonResponse(
                {"status": "error", "message": "Invalid JSON"}, status=400
            )
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    else:
        form = JoinListForm()

    # GET → render template as before
    return render(request, "index.html", {"form": form, "percent": percent})


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
