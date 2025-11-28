import requests
from PIL import Image
from io import BytesIO

url = "https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_3.png?sv=2025-07-05&spr=https&st=2025-11-24T14%3A24%3A39Z&se=2026-11-25T14%3A24%3A00Z&sr=b&sp=r&sig=egKAmIUms8H5f3kgrGXKvcfuBVlQp0Qc2tsfxdvRgUY%3D"

print("Testing direct download...")
try:
    response = requests.get(url, timeout=30, headers={'User-Agent': 'Mozilla/5.0'})
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    print(f"Content Length: {len(response.content)}")
    
    # Try to open as image
    image = Image.open(BytesIO(response.content))
    print(f"Image Size: {image.size}")
    print(f"Image Mode: {image.mode}")
    print("SUCCESS!")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
