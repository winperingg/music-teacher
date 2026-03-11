import requests
from django.conf import settings


def criar_assinatura_mercadopago(payer_email: str, external_reference: str):
    url = "https://api.mercadopago.com/preapproval"

    headers = {
        "Authorization": f"Bearer {settings.MERCADOPAGO_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    data = {
        "preapproval_plan_id": settings.MERCADOPAGO_PLAN_ID,
        "reason": "Assinatura Music Teacher",
        "payer_email": payer_email,
        "external_reference": external_reference,
        "back_url": f"{settings.SITE_URL}/assinatura/",
        "status": "pending",
    }

    response = requests.post(url, json=data, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()


def consultar_assinatura_mercadopago(preapproval_id: str):
    url = f"https://api.mercadopago.com/preapproval/{preapproval_id}"

    headers = {
        "Authorization": f"Bearer {settings.MERCADOPAGO_ACCESS_TOKEN}",
    }

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()