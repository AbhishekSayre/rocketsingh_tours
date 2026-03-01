from django.contrib.auth import get_user_model, login
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
    Must return a redirect using `strategy.redirect()`.
    """
    if user:
        # First, set backend for the user
        backend_name = kwargs.get("backend")
        if backend_name:
            user.backend = backend_name

        # Now log in the user
        login(strategy.request, user)

        required_fields = ["name", "gender", "dob", "phone"]
        missing = [f for f in required_fields if not getattr(user, f, None)]
        if missing:
            return strategy.redirect(reverse("complete_profile"))

    return None


def set_user_backend(strategy, user=None, *args, **kwargs):
    """Attach backend attribute to user for multiple backends"""
    if user:
        backend = kwargs.get('backend')
        if backend:
            # Set backend as dotted import path string
            user.backend = f"{backend.__module__}.{backend.__class__.__name__}"

