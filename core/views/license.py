import json
from datetime import datetime
from typing import ClassVar

from decouple import config
from django.http import HttpRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from core.models import Equipment, License
from core.utils.license import sign_license

EXPECTED_PASSWORD = config("LICENSE_DEFAULT_PASSWORD", default="default_password")

@method_decorator(csrf_exempt, name="dispatch")
class ActivateView(View):
    http_method_names: ClassVar[list[str]] = ["post"]

    def post(self, request: HttpRequest, serial_number: str) -> JsonResponse:
        try:
            try:
                raw_body = request.body
                data = json.loads(raw_body)
            except json.JSONDecodeError:
                return JsonResponse(
                    {
                        "status": "error",
                        "error": "Invalid JSON",
                        "raw_body": raw_body.decode(errors="replace"),
                    },
                    status=400,
                )

            required_fields = ["product", "license_password"]
            missing = [f for f in required_fields if f not in data]
            if missing:
                return JsonResponse(
                    {"status": "error", "error": f"Missing fields: {', '.join(missing)}"},
                    status=400,
                )

            product = data["product"]
            license_password = data["license_password"]
            host_hwid = data.get("host_hwid", "")
            device_hwid = data.get("device_hwid", "")
            if not host_hwid and not device_hwid:
                return JsonResponse(
                    {"status": "error", "error": "At least one HWID must be provided"},
                    status=400,
                )

            ver = data.get("ver", "")
            company_name = data.get("company_name", "")
            exp = data.get("exp", "2100-01-01")
            features = data.get("features", {})

            try:
                equipment = Equipment.objects.select_related("model").get(serial_number=serial_number)
            except Equipment.DoesNotExist:
                return JsonResponse(
                    {"status": "error", "error": f"Equipment with serial number {serial_number} not found"},
                    status=404,
                )

            if equipment.model.equipment_type.name != product:
                return JsonResponse(
                    {
                        "status": "error",
                        "error": f"Product mismatch: expected {equipment.model.equipment_type.name}, got {product}",
                    },
                    status=400,
                )

            if license_password != EXPECTED_PASSWORD:
                return JsonResponse(
                    {"status": "error", "error": "Invalid license password"},
                    status=403,
                )

            if equipment.license:
                equipment.license.delete()

            payload = {
                "ver": ver,
                "product": product,
                "company_name": company_name,
                "host_hwid": host_hwid,
                "device_hwid": device_hwid,
                "exp": exp,
                "features": features,
            }

            try:
                signed = sign_license(payload)
            except FileNotFoundError:
                return JsonResponse(
                    {"status": "error", "error": "Private key not found"},
                    status=500,
                )
            except PermissionError:
                return JsonResponse(
                    {"status": "error", "error": "No permission to read private key"},
                    status=500,
                )
            except Exception as e:
                return JsonResponse(
                    {"status": "error", "error": f"Failed to sign license: {e!s}"},
                    status=500,
                )

            try:
                exp_date = datetime.strptime(exp, "%Y-%m-%d").date()
            except (ValueError, TypeError):
                exp_date = datetime(2100, 1, 1).date()

            # 10. Создание License
            try:
                license_obj = License.objects.create(
                    ver=ver,
                    product=product,
                    company_name=company_name,
                    host_hwid=host_hwid,
                    device_hwid=device_hwid,
                    exp=exp_date,
                    features=features,
                    signature=signed.get("signature", ""),
                    license_key=signed.get("license_key", ""),
                )
            except Exception as e:
                return JsonResponse(
                    {"status": "error", "error": f"Failed to create License: {e!s}"},
                    status=500,
                )

            try:
                equipment.license = license_obj
                equipment.save(update_fields=["license"])
            except Exception as e:
                license_obj.delete()
                return JsonResponse(
                    {"status": "error", "error": f"Failed to attach license: {e!s}"},
                    status=500,
                )

            return JsonResponse(
                {
                    "status": "ok",
                    "license": {
                        "license_key": signed.get("license_key"),
                        "payload": signed.get("payload"),
                        "signature": signed.get("signature"),
                    },
                }
            )

        except Exception as e:
            return JsonResponse(
                {"status": "error", "error": f"Unhandled exception: {e!s}"},
                status=500,
            )
