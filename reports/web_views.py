# In reports/web_views.py

from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin

# Make sure to import the list of fields from your statistics_views file
from .views.statistics_views import VALID_GROUPING_FIELDS


class StatisticsPageView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):

        # Create a new list that contains the machine name and a pretty display name
        grouping_choices = []
        for field in VALID_GROUPING_FIELDS:
            # e.g., 'region__name' becomes 'Region Name'
            display_name = field.replace("__", " ").replace("_", " ").title()
            grouping_choices.append((field, display_name))

        context = {
            # Pass this new list to the template
            "grouping_choices": grouping_choices
        }
        return render(request, "reports/statistics_page.html", context)
