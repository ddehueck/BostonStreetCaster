import hashlib
import hmac
import base64
from urllib.parse import urlparse

def sign_url(input_url, secret):
    """ Sign a request URL with a URL signing secret.
        Ref: https://ppt.cc/fx

        Args:
        input_url  - The URL to sign
        secret     - URL signing secret

        Returns:
        (str) The signed request URL.
    """
    if not input_url or not secret:
        raise Exception("Both URL and secret should be non-empty string.")

    url = urlparse(input_url)
    url_to_sign = "{}?{}".format(url.path, url.query)

    decoded_key = base64.urlsafe_b64decode(secret)
    url_to_sign_encoded = url_to_sign.encode("utf-8")
    signature = hmac.new(decoded_key, url_to_sign_encoded, hashlib.sha1)

    encoded_signature = base64.urlsafe_b64encode(signature.digest()).decode("utf-8")
    signed_url_format_args = [url.scheme, url.netloc, url.path, url.query, encoded_signature]

    return "{}://{}{}?{}&signature={}".format(*signed_url_format_args)
