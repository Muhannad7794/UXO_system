# In uxo_project/views.py

from django.shortcuts import render


def index(request):
    """
    Renders the homepage. The template itself handles the logic
    for displaying content to either authenticated admins or the public.
    """
    return render(request, "index.html")
