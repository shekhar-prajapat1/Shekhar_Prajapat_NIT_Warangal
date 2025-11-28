import requests
import json

# Corrected URLs with proper hyphen: datathon-IIT
test_cases = [
    {
        "name": "Sample 3",
        "url": "https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_3.png?sv=2025-07-05&spr=https&st=2025-11-24T14%3A24%3A39Z&se=2026-11-25T14%3A24%3A00Z&sr=b&sp=r&sig=egKAmIUms8H5f3kgrGXKvcfuBVlQp0Qc2tsfxdvRgUY%3D"
    },
    {
        "name": "Sample 1",
        "url": "https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_1.png?sv=2025-07-05&spr=https&st=2025-11-24T14%3A21%3A03Z&se=2026-11-25T14%3A21%3A00Z&sr=b&sp=r&sig=2szJobwLVzcVSmg5IPWjRT9k7pHq2Tvifd6seRa2xRI%3D"
    },
    {
        "name": "Sample 2",
        "url": "https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_2.png?sv=2025-07-05&spr=https&st=2025-11-24T14%3A13%3A22Z&se=2026-11-25T14%3A13%3A00Z&sr=b&sp=r&sig=WFJYfNw0PJdZOpOYlsoAW0XujYGG1x2HSbcDREiFXSU%3D"
    }
]

api_url = "http://localhost:8001/extract-bill-data"

print("="*70)
print("TESTING ALL 3 SAMPLES")
print("="*70)

for i, test in enumerate(test_cases, 1):
    print(f"\n{'='*70}")
    print(f"TEST CASE {i}: {test['name']}")
    print("="*70)
    
    payload = {"document": test['url']}
    
    try:
        response = requests.post(api_url, json=payload, timeout=60)
        result = response.json()
        
        if result.get("is_success"):
            data = result.get("data", {})
            items = data.get("total_item_count", 0)
            amount = data.get("reconciled_amount", 0)
            
            print(f"✅ SUCCESS")
            print(f"   Total Items: {items}")
            print(f"   Reconciled Amount: ₹{amount:,.2f}")
            
            # Show first 3 items as sample
            pagewise = data.get("pagewise_line_items", [])
            if pagewise and pagewise[0].get("bill_items"):
                print(f"\n   Sample Items:")
                for item in pagewise[0]["bill_items"][:3]:
                    print(f"   • {item['item_name']}: ₹{item['item_amount']}")
                if len(pagewise[0]["bill_items"]) > 3:
                    print(f"   ... and {len(pagewise[0]['bill_items']) - 3} more items")
        else:
            print(f"❌ FAILED: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

print(f"\n{'='*70}")
print("ALL TESTS COMPLETED")
print("="*70)
