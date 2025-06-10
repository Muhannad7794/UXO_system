# In uxo_project/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import logout
from uxo_records.models import UXORecord


def index(request):
    """
    Renders the homepage. If the user is an admin, it also passes
    context data needed to build the map filtering form.
    """
    context = {}
    if request.user.is_authenticated:
        # Get the choices from the model fields to populate the filter dropdowns
        context = {
            "ordnance_type_choices": UXORecord._meta.get_field("ordnance_type").choices,
            "ordnance_condition_choices": UXORecord._meta.get_field(
                "ordnance_condition"
            ).choices,
            "burial_status_choices": UXORecord._meta.get_field("burial_status").choices,
        }
    return render(request, "index.html", context)


## Logout view
def logout_view(request):
    """
    Logs the user out and redirects to the homepage.
    """
    logout(request)
    return redirect("index")
