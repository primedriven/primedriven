from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .decorator import manager_required
from home.models import EntryLIST
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone

from baseapp import utils


@manager_required
def dashboard(request):
    context = {}
    context["entry_list"] = EntryLIST.objects.all().count()
    return render(request, "manager/index.html", context)


@manager_required
def send_email_panel(request):
    entries = EntryLIST.objects.all()
    print(entries)
    recent_logs = (
        []
    )  # swap for EmailSendLog.objects.select_related('entry').order_by('-sent_at')[:10]
    sent_today = 0  # swap for EmailSendLog.objects.filter(sent_at__date=timezone.now().date()).count()

    if request.method == "POST":
        entry_id = request.POST.get("entry_id")
        mail_type = request.POST.get(
            "mail_type"
        )  # confirmation | reminder | congratulations
        entry_number = request.POST.get("entry_number", "")
        draw_date = request.POST.get("draw_date", "")
        draw_time = request.POST.get("draw_time", "")

        if not entry_id or not mail_type:
            messages.error(request, "Please select a recipient and email type.")
            return redirect("send_email_panel")

        entry = get_object_or_404(EntryLIST, id=entry_id)

        # ── Build context for email templates ──
        context = {
            "name": entry.full_name,
            "entry_num": entry_number,
            "draw_date": draw_date,
            "draw_time": draw_time,
            "unsubscribe_url": "https://primedriven.live/",
        }

        # ── Choose template + subject + flag update ──
        template_map = {
            "confirmation": {
                "subject": "Your Entry Is Approved — Prime EVs",
                "template": "mail/entry_approved.html",
                "flag": "is_accepted",
            },
            "reminder": {
                "subject": "Draw Day Reminder — Tonight at " + draw_time,
                "template": "mail/draw_reminder.html",
                "flag": "is_draw_reminded",
            },
            "congratulations": {
                "subject": "Congratulations — You've Been Selected 🎉",
                "template": "mail/congratulations.html",
                "flag": "is_congratulations",
            },
        }

        config = template_map.get(mail_type)
        if not config:
            messages.error(request, "Invalid email type selected.")
            return redirect("send_email_panel")

        recipient_email = entry.email
        if not recipient_email:
            messages.error(request, f"{entry.full_name} has no email address on file.")
            return redirect("send_email_panel")

        # ── Render and send ──
        try:
            html_message = render_to_string(config["template"], context)
            plain_message = strip_tags(html_message)

            send_mail(
                subject=config["subject"],
                message=plain_message,
                from_email="Prime Evs <noreply@primedriven.live>",
                recipient_list=[recipient_email],
                html_message=html_message,
                fail_silently=False,
            )

            # ── Update the model flag ──
            setattr(entry, config["flag"], True)
            entry.save(update_fields=[config["flag"]])

            # ── Optional: log it ──
            # EmailSendLog.objects.create(entry=entry, mail_type=mail_type)

            messages.success(
                request, f"Email sent to {entry.full_name} ({recipient_email})"
            )

        except Exception as e:
            messages.error(request, f"Failed to send: {str(e)}")

        return redirect("send_email_panel")

    return render(
        request,
        "manager/email_panel.html",
        {
            "entries": entries,
            "recent_logs": recent_logs,
            "sent_today": sent_today,
        },
    )


@manager_required
def accept_entry_mail(request):
    if request.POST:
        # title = request.POST.get("title")
        rname = request.POST.get("rname")
        email = request.POST.get("remail")
        entry_num = request.POST.get("entry_num")
        draw_date = request.POST.get("draw_date")
        subject = "Entry Confirmed: Prime Driven Giveaway"

        context = {"name": rname, "entry_num": entry_num, "draw_date": draw_date}
        message = get_template("mail/enroll.html").render(context)
        mail = EmailMessage(
            subject=subject,
            body=message,
            from_email=utils.EMAIL_ADMIN,
            to=[email],
            reply_to=[utils.EMAIL_ADMIN],
        )
        mail.content_subtype = "html"
        mail.send(fail_silently=True)

        messages.info(request, "Mail Sent")
        return redirect("accept_entry_mail")
    return render(
        request,
        "manager/accpmail.html",
        {"action_type": "Aceept Entry And Assign Number"},
    )


@manager_required
def sweep_stakes_confim(request):

    if request.POST:
        entry_number = request.POST.get("entry_number")
        rname = request.POST.get("rname")
        email = request.POST.get("remail")
        img_name = request.POST.get("img")
        prize = request.POST.get("prize")

        subject = f"Approval Documentation for Entry #{entry_number}"

        context = {
            "name": rname,
            "img_src": f"https://primedriven.live/assets/cdn/img/{img_name}",
            "prize": prize,
        }
        message = get_template("mail/primedive_winner_email.html").render(context)
        mail = EmailMessage(
            subject=subject,
            body=message,
            from_email=utils.EMAIL_ADMIN,
            to=[email],
            reply_to=[utils.EMAIL_ADMIN],
        )
        mail.content_subtype = "html"
        mail.send(fail_silently=True)

        messages.info(request, "Mail Sent")
        return redirect("sweep_stakes_confim")
    return render(request, "manager/send_approval_email.html")


@manager_required
def send_congrat(request):
    if request.POST:
        # title = request.POST.get("title")
        rname = request.POST.get("rname")
        email = request.POST.get("remail")
        entry_number = request.POST.get("entry_num")
        subject = "Your Entry Has Been Selected 🎉"

        context = {"name": rname, "entry_number": entry_number}
        message = get_template("mail/congratulations.html").render(context)
        mail = EmailMessage(
            subject=subject,
            body=message,
            from_email=utils.EMAIL_ADMIN,
            to=[email],
            reply_to=[utils.EMAIL_ADMIN],
        )
        mail.content_subtype = "html"
        mail.send(fail_silently=True)

        messages.info(request, "Mail Sent")
        return redirect("accept_entry_mail")
    return render(
        request,
        "manager/accpmail.html",
        {"action_type": "Send Congrat to winners"},
    )


@manager_required
def send_reminder(request):
    if request.POST:
        # title = request.POST.get("title")
        rname = request.POST.get("rname")
        email = request.POST.get("remail")

        subject = "Draw Day — Tonight at 7:00 PM EST"

        context = {"name": rname}
        message = get_template("mail/draw_day.html").render(context)
        mail = EmailMessage(
            subject=subject,
            body=message,
            from_email=utils.EMAIL_ADMIN,
            to=[email],
            reply_to=[utils.EMAIL_ADMIN],
        )
        mail.content_subtype = "html"
        mail.send(fail_silently=True)

        messages.info(request, "Mail Sent")
        return redirect("send_reminder")
    return render(
        request,
        "manager/accpmail.html",
        {"action_type": "Send Reminder"},
    )
