from django.shortcuts import render, redirect
from django.contrib import messages
from .decorator import manager_required
from home.models import EntryLIST
from django.core.mail import EmailMessage
from django.template.loader import get_template

from baseapp import utils


@manager_required
def dashboard(request):
    context = {}
    context["entry_list"] = EntryLIST.objects.all().count()
    return render(request, "manager/index.html", context)


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
        {"action_type": "Aceept Entry And Assign Number"},
    )
