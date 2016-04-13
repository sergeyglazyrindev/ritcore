import hashlib
import hmac
from rit.app.conf import settings


def sha256_hexdigest(string):
    return hmac.new(
        settings.CRYPTO_SECRET_TOKEN.encode('utf8'),
        string.encode('utf8'),
        digestmod=hashlib.sha256
    ).hexdigest()
