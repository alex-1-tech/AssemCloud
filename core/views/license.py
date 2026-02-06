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
            data = json.loads(request.body)

            host_hwid = data.get("host_hwid", "")
            device_hwid = data.get("device_hwid", "")
            if not host_hwid and not device_hwid:
                return JsonResponse(
                    {"status": "error", "error": "At least one HWID must be provided"},
                    status=400,
                )

            ver = data.get("ver", "")
            product = data["product"]
            company_name = data.get("company_name", "")
            exp = data.get("exp", "2100-01-01")
            features = data.get("features", {})

            license_payload = {
                "ver": ver,
                "product": product,
                "company_name": company_name,
                "host_hwid": host_hwid,
                "device_hwid": device_hwid,
                "exp": exp,
                "features": features,
            }

            model = None
            if product == "Kalmar":
                model = Kalmar32.objects.get(serial_number=serial_number)
            elif product == "Phasar":
                model = Phasar32.objects.get(serial_number=serial_number)
            license_data = sign_license(license_payload)

            try:
                exp_date = datetime.strptime(exp, "%Y-%m-%d").date()
            except (ValueError, TypeError):
                exp_date = datetime(2100, 1, 1).date()
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

            model.license = license_obj
            model.save(update_fields=["license"])

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
        except Phasar32.DoesNotExist:
            return JsonResponse(
                {
                    "status": "error",
                    "error": f"Phasar32 with serial number {serial_number} not found",
                },
                status=404,
            )
        except Kalmar32.DoesNotExist:
            return JsonResponse(
                {
                    "status": "error",
                    "error": f"Kalmar32 with serial number {serial_number} not found",
                },
                status=404,
            )
        except KeyError as e:
            return JsonResponse(
                {"status": "error", "error": f"Missing field: {e}"},
                status=400,
            )
        except Exception as e:
            return JsonResponse(
                {"status": "error", "error": str(e)},
                status=500,
            )
