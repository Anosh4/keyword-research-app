# signaturehelper.py
import base64
import hashlib
import hmac

class Signature:
    @staticmethod
    def generate(timestamp: str, method: str, uri: str, secret_key: str) -> str:
        # ── timestamp, HTTP method, URI 사이를 '.' 으로 구분
        message = f"{timestamp}.{method}.{uri}"
        digest  = hmac.new(
            secret_key.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256
        ).digest()
        return base64.b64encode(digest).decode("utf-8")
