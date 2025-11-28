"""
Test script for the Bill Extraction API
Run this after starting the server to test with the sample bill
"""
import requests
import json

# API endpoint
API_URL = "http://localhost:8001/extract-bill-data"

# Sample bill URL from the problem statement
SAMPLE_BILL_URL = "https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_3.png?sv=2025-07-05&spr=https&st=2025-11-24T14%3A24%3A39Z&se=2026-11-25T14%3A24%3A00Z&sr=b&sp=r&sig=egKAmIUms8H5f3kgrGXKvcfuBVlQp0Qc2tsfxdvRgUY%3D"

def test_extraction():
    """Test the bill extraction API"""
    
    print("=" * 60)
    print("Testing Bill Extraction API")
    print("=" * 60)
    
    # Prepare request
    payload = {
        "document": SAMPLE_BILL_URL
    }
    
    print(f"\n📤 Sending request to: {API_URL}")
    print(f"📄 Document URL: {SAMPLE_BILL_URL[:80]}...")
    
    try:
        # Make API request
        response = requests.post(API_URL, json=payload, timeout=60)
        response.raise_for_status()
        
        # Parse response
        result = response.json()
        
        print("\n" + "=" * 60)
        print("✅ RESPONSE RECEIVED")
        print("=" * 60)
        
        # Pretty print the response
        print(json.dumps(result, indent=2))
        
        # Extract key metrics
        if result.get("is_success"):
            data = result.get("data", {})
            total_items = data.get("total_item_count", 0)
            reconciled_amount = data.get("reconciled_amount", 0)
            
            print("\n" + "=" * 60)
            print("📊 EXTRACTION SUMMARY")
            print("=" * 60)
            print(f"✓ Success: {result['is_success']}")
            print(f"✓ Total Items Extracted: {total_items}")
            print(f"✓ Reconciled Amount: ₹{reconciled_amount:.2f}")
            
            # Show individual items
            print("\n📋 Line Items:")
            for page in data.get("pagewise_line_items", []):
                print(f"\n  Page {page['page_no']}:")
                for item in page["bill_items"]:
                    qty = item.get("item_quantity", "N/A")
                    rate = item.get("item_rate", "N/A")
                    print(f"    • {item['item_name']}")
                    print(f"      Qty: {qty}, Rate: {rate}, Amount: ₹{item['item_amount']:.2f}")
        else:
            print(f"\n❌ Extraction Failed: {result.get('error')}")
        
        print("\n" + "=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to API")
        print("   Make sure the server is running: python app.py")
    except requests.exceptions.Timeout:
        print("\n❌ ERROR: Request timed out")
        print("   The API might be processing a large document")
    except requests.exceptions.RequestException as e:
        print(f"\n❌ ERROR: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_extraction()
