from services.document_processor import DocumentProcessor

url = "https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_3.png?sv=2025-07-05&spr=https&st=2025-11-24T14%3A24%3A39Z&se=2026-11-25T14%3A24%3A00Z&sr=b&sp=r&sig=egKAmIUms8H5f3kgrGXKvcfuBVlQp0Qc2tsfxdvRgUY%3D"

print("Testing DocumentProcessor.download_all_pages...")
images = DocumentProcessor.download_all_pages(url)
print(f"Result: {len(images)} images")
if images:
    print(f"First image: {images[0].size}")
else:
    print("FAILED - No images returned")
