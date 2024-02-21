import hashlib
import hmac
import logging
import os

logger = logging.getLogger()
logger.setLevel(os.environ.get("LOGGING_LEVEL", logging.INFO))


class RequestSignatureDoesNotMatchException(Exception):
    pass


class GitHubSignatureHeaderMissingException(Exception):
    pass


class SecretTokenForGitHubSignatureMissingException(Exception):
    pass


class PayloadBodyMissingException(Exception):
    pass


def verify_signature(payload_body: str, secret_token: str, signature_header: str):
    """Verify that the payload was sent from GitHub by validating SHA256.

    Raise and return 403 if not authorized.

    Args:
        payload_body: original request body to verify (request.body())
        secret_token: GitHub app webhook token (WEBHOOK_SECRET)
        signature_header: header received from GitHub (x-hub-signature-256)
    """
    if not signature_header:
        raise GitHubSignatureHeaderMissingException()
    if not secret_token:
        raise SecretTokenForGitHubSignatureMissingException()
    if not payload_body:
        raise PayloadBodyMissingException()
    hash_object = hmac.new(
        secret_token.encode("utf-8"),
        msg=payload_body.encode("utf-8"),
        digestmod=hashlib.sha256,
    )
    expected_signature = "sha256=" + hash_object.hexdigest()
    if not hmac.compare_digest(expected_signature, signature_header):
        logger.debug(f"Expected signature: {expected_signature}")
        logger.debug(f"Actual signature: {signature_header}")
        raise RequestSignatureDoesNotMatchException()

    return True
