from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin

# This import is crucial. It must get the lists from your API view file.
from .views.statistics_views import (
    VALID_GROUPING_FIELDS,
    VALID_NUMERIC_FIELDS,
    AGGREGATION_MAP,
)


class StatisticsPageView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = {
            "grouping_choices": self._prepare_choices(VALID_GROUPING_FIELDS),
            "numeric_choices": self._prepare_choices(VALID_NUMERIC_FIELDS),
            "agg_op_choices": AGGREGATION_MAP.keys(),
        }
        return render(request, "reports/statistics_page.html", context)

    def _prepare_choices(self, field_list):
        choices = []
        for field in field_list:
            display_name = field.replace("__", " ").replace("_", " ").title()
            choices.append({"value": field, "name": display_name})
        return choices
