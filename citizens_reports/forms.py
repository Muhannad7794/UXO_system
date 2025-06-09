from django import forms
from uxo_records.models import UXORecord


class ReportVerificationForm(forms.Form):
    """
    A Django Form dedicated to rendering the HTML for the verification page.
    """

    ordnance_type = forms.ChoiceField(
        choices=UXORecord._meta.get_field("ordnance_type").choices,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    ordnance_condition = forms.ChoiceField(
        choices=UXORecord._meta.get_field("ordnance_condition").choices,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    is_loaded = forms.BooleanField(
        label="Is the ordnance considered to be loaded and fuzed?",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )
    proximity_to_civilians = forms.ChoiceField(
        choices=UXORecord._meta.get_field("proximity_to_civilians").choices,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    burial_status = forms.ChoiceField(
        choices=UXORecord._meta.get_field("burial_status").choices,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
