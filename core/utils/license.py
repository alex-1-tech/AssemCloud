import base64
import json

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

PRIVATE_KEY_PATH = "/opt/license/private.pem"


def load_private_key():
    with open(PRIVATE_KEY_PATH, "rb") as f:
        return serialization.load_pem_private_key(
            f.read(),
            password=None,
        )


def to_base64url(data_bytes: bytes) -> str:
    """Конвертация base64 в base64url."""
    return (
        base64.b64encode(data_bytes)
        .decode("utf-8")
        .replace("+", "-")
        .replace("/", "_")
        .rstrip("=")
    )


def sign_license(payload: dict) -> dict:
    """Подписывает лицензию и возвращает данные лицензии."""
    private_key = load_private_key()

    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()

    signature = private_key.sign(
        canonical,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )

    payload_b64 = to_base64url(canonical)
    signature_b64 = to_base64url(signature)

    license_key = f"{payload_b64}.{signature_b64}"

    return {
        "payload": payload,
        "signature": base64.b64encode(signature).decode(),
        "signature_b64url": signature_b64,
        "payload_b64url": payload_b64,
        "license_key": license_key,
        "canonical": canonical.decode("utf-8"),
    }
