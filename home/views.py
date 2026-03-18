import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.contrib import messages
from home.forms import JoinListForm


def home_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            form = JoinListForm(data)

            if form.is_valid():
                form.save()

                return JsonResponse(
                    {
                        "status": "success",
                        "message": "Entry submitted successfully! We’ll reach out to you shortly 🎉",
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
    return render(request, "index.html", {"form": form})


def rules_page(request):
    return render(request, "regulations.html")


def livedraw_page(request):
    return render(request, "livedraw.html")
