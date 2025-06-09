# In uxo_project/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import logout


def index(request):
    """
    Renders the homepage. The template itself handles the logic
    for displaying content to either authenticated admins or the public.
    """
    return render(request, "index.html")


## Logout view
def logout_view(request):
    """
    Logs the user out and redirects to the homepage.
    """
    logout(request)
    return redirect("index")
