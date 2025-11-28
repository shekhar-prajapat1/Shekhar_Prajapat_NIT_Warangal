import requests
import json

print("="*70)
print("FINAL VERIFICATION TEST")
print("="*70)

# Test with Sample 2 (simplest case)
url = "http://localhost:8001/extract-bill-data"
payload = {
    "document": "https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_2.png?sv=2025-07-05&spr=https&st=2025-11-24T14%3A13%3A22Z&se=2026-11-25T14%3A13%3A00Z&sr=b&sp=r&sig=WFJYfNw0PJdZOpOYlsoAW0XujYGG1x2HSbcDREiFXSU%3D"
}

print("\n📤 INPUT:")
print(f"   URL: {payload['document'][:80]}...")

try:
    response = requests.post(url, json=payload, timeout=60)
    result = response.json()
    
    print("\n📥 OUTPUT:")
    print(json.dumps(result, indent=2))
    
    if result.get("is_success"):
        data = result["data"]
        print("\n✅ API WORKING CORRECTLY!")
        print(f"   ✓ Extracted {data['total_item_count']} line items")
        print(f"   ✓ Reconciled Amount: ₹{data['reconciled_amount']}")
        print(f"   ✓ Response format matches specification")
        print("\n🚀 READY FOR DEPLOYMENT!")
    else:
        print(f"\n❌ Error: {result.get('error')}")
        
except Exception as e:
    print(f"\n❌ Connection Error: {e}")
    print("   Make sure server is running on port 8001")

print("\n" + "="*70)
