from django.shortcuts import redirect
from django.urls import reverse
from social_django.middleware import SocialAuthExceptionMiddleware
from social_core.exceptions import AuthAlreadyAssociated


class GoogleAuthAlreadyAssociatedMiddleware(SocialAuthExceptionMiddleware):
    """Redirect users to desired-url when AuthAlreadyAssociated exception occurs."""

    def process_exception(self, request, exception):
        if isinstance(exception, AuthAlreadyAssociated):
            if request.backend.name == "google-oauth2":
                message = "This google account is already in use."
                if message in str(exception):
                    # Add logic if required

                    # User is redirected to any url you want
                    # in this case to "app_name:url_name"
                    return redirect(reverse("oth:index"))
