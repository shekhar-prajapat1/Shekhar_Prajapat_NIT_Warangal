import requests
import json

url = "http://localhost:8001/extract-bill-data"
payload = {
    "document": "https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_3.png?sv=2025-07-05&spr=https&st=2025-11-24T14%3A24%3A39Z&se=2026-11-25T14%3A24%3A00Z&sr=b&sp=r&sig=egKAmIUms8H5f3kgrGXKvcfuBVlQp0Qc2tsfxdvRgUY%3D"
}

response = requests.post(url, json=payload, timeout=60)
result = response.json()

print(json.dumps(result, indent=2))

if result.get("is_success"):
    data = result.get("data", {})
    print(f"\n✓ Total Items: {data.get('total_item_count')}")
    print(f"✓ Reconciled Amount: {data.get('reconciled_amount')}")
    print(f"\n⚠️ Expected Total from Bill Image: 16,390.00")
