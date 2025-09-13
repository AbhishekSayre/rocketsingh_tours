from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.urls import reverse

User = get_user_model()

def save_profile(backend, user, response, *args, **kwargs):
    """Fill CustomUser fields from Google response if available"""
    if backend.name == "google-oauth2":
        user.email = response.get("email", user.email)
        user.name = response.get("name", user.name)
        # Google may not give phone/dob/gender → user will complete later
        user.save()

def redirect_if_profile_incomplete(strategy, user=None, *args, **kwargs):
    """
    After Google login, check if profile is complete.
    Redirect to complete_profile if any required field is missing.
    """
    if user:
        required_fields = ["name", "gender", "dob", "phone"]  # adjust to your CustomUser
        missing = [f for f in required_fields if not getattr(user, f, None)]
        if missing:
            return redirect(reverse("complete_profile"))