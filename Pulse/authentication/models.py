from django.db import models
from django.conf import settings
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken


class LoginSession(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='login_sessions'
    )
    jti = models.CharField(max_length=255, unique=True, db_index=True)
    user_agent = models.TextField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_revoked(self) -> bool:
        return BlacklistedToken.objects.filter(token__jti=self.jti).exists()

    def __str__(self):
        return f"{self.user} | {self.jti}"
