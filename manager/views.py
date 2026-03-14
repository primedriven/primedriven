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
        title = request.POST.get("title")
        rname = request.POST.get("rname")
        email = request.POST.get("remail")

        context = {
            "name": rname,
        }
        message = get_template("mail/enroll.html").render(context)
        mail = EmailMessage(
            subject=title,
            body=message,
            from_email=utils.EMAIL_ADMIN,
            to=[email],
            reply_to=[utils.EMAIL_ADMIN],
        )
        mail.content_subtype = "html"
        mail.send(fail_silently=True)

        messages.info(request, "Mail Sent")
        return redirect("send_message")
    return render(request, "manager/accpmail.html")
