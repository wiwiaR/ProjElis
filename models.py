import requests, json, os

accessToken = os.getenv("ASAAS_ERIRMARA_KEY")


def post_pagamento(row, index):
    url = "https://api.asaas.com/v3/payments"

    payload = {
        "billingType": "BOLETO",
        "installmentCount": int(row["installmentCount"]),
        "customer": str(row["customer"]),
        "installmentValue": float(row["value"]),
        "dueDate": str(row["dueDate"]),
        "description": str(row["description"]),
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "access_token": accessToken
    }

    try:
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            print(f"✅ Pagamento {index} enviado com sucesso!")
        else:
            print(f"❌ Erro no pagamento {index}: {response.status_code}, mensagem {response.text}")

    except Exception as e:
        print(f"❌ Exception no pagamento {index}: {e}")
