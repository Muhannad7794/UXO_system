# In uxo_project/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import logout
from uxo_records.models import UXORecord
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.core.exceptions import PermissionDenied


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
            # ADD THESE TWO LINES
            "burial_status_choices": UXORecord._meta.get_field("burial_status").choices,
            "proximity_to_civilians_choices": UXORecord._meta.get_field(
                "proximity_to_civilians"
            ).choices,
        }
    return render(request, "index.html", context)


## Logout view
def logout_view(request):
    """
    Logs the user out and redirects to the homepage.
    """
    logout(request)
    return redirect("index")


class DataImportView(LoginRequiredMixin, TemplateView):
    template_name = "data_import.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Check if the user is an admin/staff
        if not self.request.user.is_staff:
            # If not, raise a PermissionDenied exception
            raise PermissionDenied("You do not have access to this page.")
        context["title"] = "Bulk Data Import"
        return context
