import json
from datetime import datetime
from typing import ClassVar

from django.http import HttpRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from core.models import Kalmar32, License, Phasar32
from core.utils.license import sign_license

@method_decorator(csrf_exempt, name="dispatch")
class ActivateView(View):
    http_method_names: ClassVar[list[str]] = ["post"]

    def post(self, request: HttpRequest, serial_number: str) -> JsonResponse:
        try:
            try:
                raw_body = request.body
                data = json.loads(raw_body)
            except json.JSONDecodeError as e:
                return JsonResponse(
                    {"status": "error", "error": "Invalid JSON", "raw_body": raw_body.decode(errors="replace")},
                    status=400,
                )

            host_hwid = data.get("host_hwid", "")
            device_hwid = data.get("device_hwid", "")
            if not host_hwid and not device_hwid:
                return JsonResponse(
                    {"status": "error", "error": "At least one HWID must be provided"},
                    status=400,
                )

            try:
                ver = data.get("ver", "")
                product = data["product"]
                company_name = data.get("company_name", "")
                exp = data.get("exp", "2100-01-01")
                features = data.get("features", {})
            except KeyError as e:
                return JsonResponse(
                    {"status": "error", "error": f"Missing field: {e}"},
                    status=400,
                )

            license_payload = {
                "ver": ver,
                "product": product,
                "company_name": company_name,
                "host_hwid": host_hwid,
                "device_hwid": device_hwid,
                "exp": exp,
                "features": features,
            }

            try:
                if product == "Kalmar":
                    model = Kalmar32.objects.get(serial_number=serial_number)
                elif product == "Phasar":
                    model = Phasar32.objects.get(serial_number=serial_number)
                else:
                    return JsonResponse(
                        {"status": "error", "error": f"Unknown product type: {product}"},
                        status=400,
                    )
            except Phasar32.DoesNotExist:
                return JsonResponse(
                    {"status": "error", "error": f"Phasar32 with serial number {serial_number} not found"},
                    status=404,
                )
            except Kalmar32.DoesNotExist:
                return JsonResponse(
                    {"status": "error", "error": f"Kalmar32 with serial number {serial_number} not found"},
                    status=404,
                )
            except Exception as e:
                return JsonResponse(
                    {"status": "error", "error": f"Database error: {str(e)}"},
                    status=500,
                )

            try:
                license_data = sign_license(license_payload)
            except FileNotFoundError:
                return JsonResponse(
                    {"status": "error", "error": f"Private key not found"},
                    status=500,
                )
            except PermissionError:
                return JsonResponse(
                    {"status": "error", "error": f"No permission to read private key"},
                    status=500,
                )
            except Exception as e:
                return JsonResponse(
                    {"status": "error", "error": f"Failed to sign license: {str(e)}"},
                    status=500,
                )

            try:
                exp_date = datetime.strptime(exp, "%Y-%m-%d").date()
            except (ValueError, TypeError):
                exp_date = datetime(2100, 1, 1).date()

            try:
                license_obj = License.objects.create(
                    ver=ver,
                    product=product,
                    company_name=company_name,
                    host_hwid=host_hwid,
                    device_hwid=device_hwid,
                    exp=exp_date,
                    features=features,
                    signature=license_data.get("signature", ""),
                    license_key=license_data.get("license_key", ""),
                )
            except Exception as e:
                return JsonResponse(
                    {"status": "error", "error": f"Failed to create License object: {str(e)}"},
                    status=500,
                )

            try:
                model.license = license_obj
                model.save(update_fields=["license"])
            except Exception as e:
                return JsonResponse(
                    {"status": "error", "error": f"Failed to attach license to device: {str(e)}"},
                    status=500,
                )

            try:
                return JsonResponse(
                    {
                        "status": "ok",
                        "license": {
                            "license_key": license_data.get("license_key"),
                            "payload": license_data.get("payload"),
                            "signature": license_data.get("signature"),
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
