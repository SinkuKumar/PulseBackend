from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import get_authorization_header


class CookieJWTAuthentication(JWTAuthentication):
    """
    Reads JWT access token from HttpOnly cookie if no Authorization header exists.
    """
    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        # If Authorization header is missing, pull access token from cookie
        if not auth:
            access = request.COOKIES.get("access_token")
            if access:
                request.META["HTTP_AUTHORIZATION"] = f"Bearer {access}"

        return super().authenticate(request)
