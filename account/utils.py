from .models import BlacklistedToken


def blacklist_token(token):
    # Add token to the blacklist
    BlacklistedToken.objects.create(token=token)
