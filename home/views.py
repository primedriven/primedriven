from django.shortcuts import render, redirect
from django.contrib import messages
from home.forms import JoinListForm


def home_view(request):
    if request.method == "POST":
        form = JoinListForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thank you! Entry Submitted successfully 🎉")
            return redirect(request.path)
    else:
        form = JoinListForm()

    return render(request, "index.html", {"form": form})


def rules_page(request):
    return render(request, "regulations.html")
