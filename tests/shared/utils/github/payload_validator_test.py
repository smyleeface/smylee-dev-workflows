import json
import pytest

from dev_workflow.utils.github.payload_validator import verify_signature
from dev_workflow.utils.github.payload_validator import (
    RequestSignatureDoesNotMatchException,
    GitHubSignatureHeaderMissingException,
    SecretTokenForGitHubSignatureMissingException,
    PayloadBodyMissingException,
)


def test_verify_signature():
    payload_body = '{"foo":"bar","number":5,"status":{"active":true}}'
    secret_token = "abc"
    signature_header = "sha256=5beff85e67f5a4da6bd1e3c9f01a7f99bc9aa59f140f58ecb9cae0831b5daa4b"

    # test with valid signature
    assert verify_signature(payload_body, secret_token, signature_header)

    # test with invalid signature
    with pytest.raises(RequestSignatureDoesNotMatchException):
        verify_signature(payload_body, secret_token, "invalid_signature")

    # test with missing signature header
    with pytest.raises(GitHubSignatureHeaderMissingException):
        verify_signature(payload_body, secret_token, None)

    # test with missing payload body
    with pytest.raises(PayloadBodyMissingException):
        verify_signature(None, secret_token, signature_header)

    # test with missing secret token
    with pytest.raises(SecretTokenForGitHubSignatureMissingException):
        verify_signature(payload_body, None, signature_header)
