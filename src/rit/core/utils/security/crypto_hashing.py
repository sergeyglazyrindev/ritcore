import hashlib
import hmac
from rit.app.conf import settings


def generate_sha256_password(password):
    return hmac.new(
        settings.CRYPTO_SECRET_TOKEN.encode('utf8'),
        password.encode('utf8'),
        digestmod=hashlib.sha256
    ).hexdigest()
