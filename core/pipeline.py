from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

def save_profile(backend, user, response, *args, **kwargs):
    """
    Fill CustomUser fields from Google response if available.
    This runs during the social-auth pipeline after user is created/logged in.
    """
    if backend.name == "google-oauth2":
        user.email = response.get("email", user.email)
        user.name = response.get("name", user.name)
        # Google usually doesn't provide phone/dob/gender
        user.save()

def redirect_if_profile_incomplete(strategy, user=None, *args, **kwargs):
    """
    After Google login, check if profile is complete.
    Redirect to complete_profile if any required field is missing.
    """
    if user:
        required_fields = ["name", "gender", "dob", "phone"]
        missing = [f for f in required_fields if not getattr(user, f, None)]
        if missing:
            # ✅ Correct way to redirect in python-social-auth
            return strategy.redirect(reverse("complete_profile"))
