"""License utilities for signing, generating, and attaching licenses to Equipment (unified model).

This module provides functions for loading private keys, signing license payloads,
and generating licenses for unified Equipment, including error handling and database integration.
"""

import base64
import json
from datetime import datetime
from pathlib import Path

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from django.http import HttpRequest, JsonResponse

from core.models import Equipment, License

PRIVATE_KEY_PATH = "/opt/license/private.pem"


def load_private_key() -> rsa.RSAPrivateKey:
    """Load the private key for signing licenses."""
    with Path.open(PRIVATE_KEY_PATH, "rb") as f:
        return load_pem_private_key(f.read(), password=None)


def sign_license(payload: dict) -> dict:
    """Sign the license payload and return the license data."""
    private_key = load_private_key()

    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )

    if isinstance(private_key, rsa.RSAPrivateKey):
        signature = private_key.sign(canonical, padding.PKCS1v15(), hashes.SHA256())

        public_key = private_key.public_key()
        public_key.verify(signature, canonical, padding.PKCS1v15(), hashes.SHA256())
    else:
        signature = private_key.sign(canonical, hashes.SHA256())

    canonical_b64 = base64.urlsafe_b64encode(canonical).decode("utf-8")
    signature_b64 = base64.urlsafe_b64encode(signature).decode("utf-8")

    license_key = f"{canonical_b64}.{signature_b64}"

    return {
        "payload": payload,
        "signature": signature_b64,
        "license_key": license_key,
    }


def generate_license_view(request: HttpRequest, serial_number: str) -> JsonResponse:
    """Django view to generate a license for a unified Equipment instance."""
    try:
        try:
            raw_body = request.body
            data = json.loads(raw_body)
        except json.JSONDecodeError:
            return JsonResponse(
                {"status": "error", "error": "Invalid JSON", "raw_body": raw_body.decode(errors="replace")},
                status=400,
            )

        required_fields = ["product", "company_name", "exp"]
        missing_fields = [f for f in required_fields if f not in data]
        if missing_fields:
            return JsonResponse(
                {"status": "error", "error": f"Missing required fields: {', '.join(missing_fields)}"},
                status=400,
            )

        try:
            license_payload = {
                "ver": data.get("ver", "1.0.0"),
                "product": data["product"],
                "company_name": data["company_name"],
                "host_hwid": data.get("host_hwid", ""),
                "device_hwid": data.get("device_hwid", ""),
                "exp": data["exp"],
                "features": data.get("features", {}),
            }
        except Exception as e:
            return JsonResponse(
                {"status": "error", "error": f"Failed to prepare license payload: {e!s}"},
                status=500,
            )

        try:
            license_data = sign_license(license_payload)
        except FileNotFoundError:
            return JsonResponse(
                {"status": "error", "error": f"Private key not found at {PRIVATE_KEY_PATH}"},
                status=500,
            )
        except PermissionError:
            return JsonResponse(
                {"status": "error", "error": f"No permission to read private key at {PRIVATE_KEY_PATH}"},
                status=500,
            )
        except Exception as e:
            return JsonResponse(
                {"status": "error", "error": f"Failed to sign license: {e!s}"},
                status=500,
            )

        try:
            equipment = Equipment.objects.select_related("model").get(serial_number=serial_number)
        except Equipment.DoesNotExist:
            return JsonResponse(
                {"status": "error", "error": f"Equipment with serial number {serial_number} not found"},
                status=404,
            )
        except Exception as e:
            return JsonResponse(
                {"status": "error", "error": f"Database error retrieving device: {e!s}"},
                status=500,
            )

        if equipment.model.name != license_payload["product"]:
            return JsonResponse(
                {"status": "error", "error": f"Product mismatch: expected {equipment.model.name}, got {license_payload['product']}"},
                status=400,
            )

        if equipment.license:
            equipment.license.delete()

        try:
            exp_date = datetime.strptime(license_payload["exp"], "%Y-%m-%d").date()
        except (ValueError, TypeError):
            exp_date = datetime(2100, 1, 1).date()

        try:
            license_obj = License.objects.create(
                ver=license_payload["ver"],
                product=license_payload["product"],
                company_name=license_payload["company_name"],
                host_hwid=license_payload["host_hwid"],
                device_hwid=license_payload["device_hwid"],
                exp=exp_date,
                features=license_payload["features"],
                signature=license_data.get("signature", ""),
                license_key=license_data.get("license_key", ""),
            )
        except Exception as e:
            return JsonResponse(
                {"status": "error", "error": f"Failed to create License object: {e!s}"},
                status=500,
            )

        try:
            equipment.license = license_obj
            equipment.save(update_fields=["license"])
        except Exception as e:
            license_obj.delete()  # откат
            return JsonResponse(
                {"status": "error", "error": f"Failed to attach license to equipment: {e!s}"},
                status=500,
            )

        try:
            return JsonResponse(
                {
                    "status": "ok",
                    "license": license_data,
                    "equipment": {
                        "serial_number": equipment.serial_number,
                        "shipment_date": (
                            equipment.shipment_date.isoformat() if equipment.shipment_date else None
                        ),
                    },
                }
            )
        except Exception as e:
            return JsonResponse(
                {"status": "error", "error": f"Failed to serialize response: {e!s}"},
                status=500,
            )

    except Exception as e:
        return JsonResponse(
            {"status": "error", "error": f"Unhandled exception: {e!s}"},
            status=500,
        )