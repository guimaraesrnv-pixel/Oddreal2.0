
import hashlib


class Security:

    @staticmethod
    def sha256(text: str):

        return hashlib.sha256(

            text.encode()

        ).hexdigest()
