from django.urls import path
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.reverse import reverse

from .views import (
    LoginView,
    RefreshView,
    LogoutView,
    AuthStatusView,
    SessionsListView,
    RevokeSessionView
)


class AuthRootView(APIView):
    """
    Authentication API Root
    Provides documentation and hyperlinks to all auth-related endpoints.
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        return Response({
            "status": reverse("auth-status", request=request),
            "login": reverse("auth-login", request=request),
            "refresh": reverse("auth-refresh", request=request),
            "logout": reverse("auth-logout", request=request),
            "sessions_list": reverse("auth-sessions", request=request),
            "session_revoke_example": reverse("auth-revoke-session", args=["<jti>"], request=request),
        })


urlpatterns = [
    path("", AuthRootView.as_view(), name="auth-root"),
    path("status/", AuthStatusView.as_view(), name="auth-status"),
    path("login/", LoginView.as_view(), name="auth-login"),
    path("refresh/", RefreshView.as_view(), name="auth-refresh"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    path("session/", SessionsListView.as_view(), name="auth-sessions"),
    path("session/revoke/<jti>", RevokeSessionView.as_view(), name="auth-revoke-session")
]
