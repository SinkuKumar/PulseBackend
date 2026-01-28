from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework import status, permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken

from rest_framework_simplejwt.token_blacklist.models import (
    OutstandingToken,
    BlacklistedToken
)

from rest_framework.permissions import AllowAny

from .models import LoginSession
from authentication.serializers import LoginSessionSerializer


ACCESS_COOKIE_NAME = "access_token"
REFRESH_COOKIE_NAME = "refresh_token"
COOKIE_AGE = 7 * 24 * 60 * 60  # 7 days


def _set_cookie(response, key, value, max_age):
    response.set_cookie(
        key=key,
        value=value,
        max_age=max_age,
        httponly=True,
        secure=True,
        samesite="Strict",
        path="/"
    )


class AuthStatusView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        access_token = (
            request.COOKIES.get(ACCESS_COOKIE_NAME)
            or request.headers.get("Authorization", "").replace("Bearer ", "")
        )

        if not access_token:
            return Response(
                {"authenticated": False},
                status=status.HTTP_200_OK
            )

        try:
            token = AccessToken(access_token)
        except TokenError:
            return Response(
                {"authenticated": False},
                status=status.HTTP_200_OK
            )

        # Optional but recommended if you blacklist access tokens
        if BlacklistedToken.objects.filter(token__jti=token["jti"]).exists():
            return Response(
                {"authenticated": False},
                status=status.HTTP_200_OK
            )

        return Response(
            {
                "authenticated": True,
                "user_id": token.get("user_id"),
            },
            status=status.HTTP_200_OK
        )


class LoginView(TokenObtainPairView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        user_agent = request.headers.get("User-Agent", "")
        ip = self._get_client_ip(request)

        response = super().post(request, *args, **kwargs)
        if response.status_code != 200:
            return response

        tokens = response.data
        refresh = RefreshToken(tokens["refresh"])
        access = tokens["access"]

        User = get_user_model()
        user = get_object_or_404(User, pk=refresh["user_id"])

        LoginSession.objects.create(
            user=user,
            jti=refresh["jti"],
            user_agent=user_agent,
            ip_address=ip,
        )

        res = Response({"detail": "Login successful"}, status=status.HTTP_200_OK)
        _set_cookie(res, ACCESS_COOKIE_NAME, access, max_age=15 * 60)
        _set_cookie(res, REFRESH_COOKIE_NAME, str(refresh), max_age=COOKIE_AGE)
        return res

    def _get_client_ip(self, request):
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        if xff:
            return xff.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")


class RefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = (
            request.COOKIES.get(REFRESH_COOKIE_NAME)
            or request.data.get("refresh")
        )

        if not refresh_token:
            return Response(
                {"detail": "No refresh token provided"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            token = RefreshToken(refresh_token)
        except TokenError:
            return Response(
                {"detail": "Invalid token"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Blacklist check (authoritative)
        if BlacklistedToken.objects.filter(token__jti=token["jti"]).exists():
            return Response(
                {"detail": "Token revoked"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        serializer = self.get_serializer(data={"refresh": refresh_token})
        serializer.is_valid(raise_exception=True)

        access = serializer.validated_data["access"]
        new_refresh = serializer.validated_data.get("refresh")

        res = Response({"detail": "Token refreshed"}, status=status.HTTP_200_OK)
        _set_cookie(res, ACCESS_COOKIE_NAME, access, max_age=15 * 60)

        if new_refresh:
            _set_cookie(
                res,
                REFRESH_COOKIE_NAME,
                str(new_refresh),
                max_age=COOKIE_AGE
            )

        return res


class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        refresh_token = (
            request.COOKIES.get(REFRESH_COOKIE_NAME)
            or request.data.get("refresh")
        )

        if not refresh_token:
            return Response(
                {"detail": "No refresh token"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            res = Response({"detail": "Logged out"}, status=status.HTTP_200_OK)
            res.delete_cookie(ACCESS_COOKIE_NAME, path="/")
            res.delete_cookie(REFRESH_COOKIE_NAME, path="/")
            return res

        except TokenError:
            return Response(
                {"detail": "Invalid token"},
                status=status.HTTP_400_BAD_REQUEST
            )


class SessionsListView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = LoginSessionSerializer

    def get_queryset(self):
        return LoginSession.objects.filter(
            user=self.request.user
        ).order_by("-created_at")


class RevokeSessionView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def delete(self, request, jti):
        try:
            session = LoginSession.objects.get(
                user=request.user,
                jti=jti
            )
        except LoginSession.DoesNotExist:
            return Response(
                {"detail": "Session not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            outstanding = OutstandingToken.objects.get(jti=jti)
            BlacklistedToken.objects.get_or_create(token=outstanding)
        except OutstandingToken.DoesNotExist:
            pass

        return Response(
            {"detail": "Session revoked"},
            status=status.HTTP_200_OK
        )
