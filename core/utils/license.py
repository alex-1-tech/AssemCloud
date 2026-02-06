import base64
import json

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from django.http import HttpRequest, JsonResponse

from core.models import Kalmar32, License

PRIVATE_KEY_PATH = "/opt/license/private.pem"


def load_private_key():
    with open(PRIVATE_KEY_PATH, "rb") as f:
        return load_pem_private_key(f.read(), password=None)


def sign_license(payload: dict) -> dict:
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


def generate_license_view(self, request: HttpRequest, serial_number: str) -> JsonResponse:
    try:
        try:
            raw_body = request.body
            data = json.loads(raw_body)
        except json.JSONDecodeError as e:
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
                {"status": "error", "error": f"Failed to prepare license payload: {str(e)}"},
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
                {"status": "error", "error": f"Failed to sign license: {str(e)}"},
                status=500,
            )

        try:
            kalmar32 = Kalmar32.objects.get(serial_number=serial_number)
        except Kalmar32.DoesNotExist:
            return JsonResponse(
                {"status": "error", "error": f"Kalmar32 with serial number {serial_number} not found"},
                status=404,
            )
        except Exception as e:
            return JsonResponse(
                {"status": "error", "error": f"Database error retrieving device: {str(e)}"},
                status=500,
            )

        try:
            license_obj = License.objects.create(
                ver=license_payload["ver"],
                product=license_payload["product"],
                company_name=license_payload["company_name"],
                host_hwid=license_payload["host_hwid"],
                device_hwid=license_payload["device_hwid"],
                exp=license_payload["exp"],
                features=license_payload["features"],
                signature=license_data.get("signature", ""),
                license_key=license_data.get("license_key", ""),
            )
        except Exception as e:
            return JsonResponse(
                {"status": "error", "error": f"Failed to create License object: {str(e)}"},
                status=500,
            )

        try:
            kalmar32.license = license_obj
            kalmar32.save()
        except Exception as e:
            return JsonResponse(
                {"status": "error", "error": f"Failed to attach license to device: {str(e)}"},
                status=500,
            )

        try:
            return JsonResponse(
                {
                    "status": "ok",
                    "license": license_data,
                    "equipment": {
                        "serial_number": kalmar32.serial_number,
                        "shipment_date": kalmar32.shipment_date.isoformat() if kalmar32.shipment_date else None,
                    },
                }
            )
        except Exception as e:
            return JsonResponse(
                {"status": "error", "error": f"Failed to serialize response: {str(e)}"},
                status=500,
            )

    except Exception as e:
        return JsonResponse(
            {"status": "error", "error": f"Unhandled exception: {str(e)}"},
            status=500,
        )

