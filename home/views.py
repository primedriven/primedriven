from django.shortcuts import render


def home_view(request):
    return render(request, "index.html")


def rules_page(request):
    return render(request, "regulations.html")
