from django.contrib.auth import get_user_model,login
from django.shortcuts import redirect
from django.urls import reverse

User = get_user_model()

def save_profile(backend, user, response, *args, **kwargs):
    """Fill CustomUser fields from Google response if available"""
    if backend.name == "google-oauth2":
        user.email = response.get("email", user.email)
        user.name = response.get("name", user.name)
        user.save()

def redirect_if_profile_incomplete(strategy, backend, user=None, *args, **kwargs):
    """
    After Google login, redirect user to complete_profile if profile incomplete.
    Must return a redirect using `strategy.redirect()` for python-social-auth.
    """
    if user:
        login(strategy.request, user)  # log in the user
        required_fields = ["name", "gender", "dob", "phone"]
        missing = [f for f in required_fields if not getattr(user, f, None)]
        if missing:
            # Stop the pipeline and redirect
            return strategy.redirect(reverse("complete_profile"))
        else:
            return redirect("home")
