from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.exceptions import ValidationError
from .models import UserToken, BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken


class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None
        access_token = request.headers.get("Authorization")

        validated_token = self.get_validated_token(raw_token)
        user = self.get_user(validated_token)
        if access_token and access_token.startswith("Bearer "):
            access_token = access_token.split("Bearer ")[1]

        # Ensure the raw_token is in a string format that matches stored tokens
        raw_token_str = (
            raw_token.decode("utf-8")
            if isinstance(raw_token, bytes)
            else str(raw_token)
        )
        if BlacklistedToken.objects.filter(token=raw_token_str).exists():
            raise AuthenticationFailed(
                "Authentication credentials were not provided or are invalid."
            )

        # Invalidate the oldest refresh token if needed
        self.invalidate_oldest_refresh_token(user, raw_token_str)

        return user, validated_token

    def invalidate_oldest_refresh_token(self, user, new_refresh_token):
        refresh_tokens = UserToken.objects.filter(user=user).order_by("created_at")

        if refresh_tokens.count() > 1:
            oldest_token = refresh_tokens.first()

            BlacklistedToken.objects.get_or_create(token=oldest_token.token)

            oldest_token.delete()
