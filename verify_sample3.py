import requests
import json

url = "http://localhost:8001/extract-bill-data"
payload = {
    "document": "https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_3.png?sv=2025-07-05&spr=https&st=2025-11-24T14%3A24%3A39Z&se=2026-11-25T14%3A24%3A00Z&sr=b&sp=r&sig=egKAmIUms8H5f3kgrGXKvcfuBVlQp0Qc2tsfxdvRgUY%3D"
}

print("Testing Sample 3 extraction...")
print("="*60)

response = requests.post(url, json=payload, timeout=60)
result = response.json()

print(json.dumps(result, indent=2))

if result.get("is_success"):
    data = result.get("data", {})
    reconciled = data.get('reconciled_amount')
    count = data.get('total_item_count')
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total Items Extracted: {count}")
    print(f"Reconciled Amount: ₹{reconciled}")
    print(f"Expected Total (from image): ₹16,390.00")
    
    if reconciled == 16390.0:
        print("\n✅ CORRECT! Amounts match perfectly.")
    else:
        diff = abs(reconciled - 16390.0)
        print(f"\n⚠️ MISMATCH! Difference: ₹{diff}")
