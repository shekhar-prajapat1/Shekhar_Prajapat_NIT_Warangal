import requests
from PIL import Image
from io import BytesIO
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Handles document downloading and preprocessing"""
    
    @staticmethod
    def download_image(url: str) -> Optional[Image.Image]:
        """
        Download image from URL (returns first page for PDFs)
        
        Args:
            url: URL of the image to download
            
        Returns:
            PIL Image object or None if download fails
        """
        images = DocumentProcessor.download_all_pages(url)
        return images[0] if images else None
    
    @staticmethod
    def download_all_pages(url: str) -> list[Image.Image]:
        """
        Download all pages from a document URL (supports multi-page PDFs)
        
        Args:
            url: URL of the document to download
            
        Returns:
            List of PIL Image objects (one per page)
        """
        try:
            logger.info(f"Downloading document from: {url}")
            response = requests.get(url, timeout=30, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
            
            content_type = response.headers.get('Content-Type', '').lower()
            url_lower = url.lower()
            
            # Check if it's a PDF (by content-type or extension)
            is_pdf = ('application/pdf' in content_type or 
                     url_lower.endswith('.pdf') or
                     response.content[:4] == b'%PDF')
            
            if is_pdf:
                try:
                    from pdf2image import convert_from_bytes
                    logger.info("Detected PDF document, converting to images...")
                    # Convert ALL pages of PDF to images
                    images = convert_from_bytes(response.content, dpi=200)
                    if images:
                        logger.info(f"Successfully converted PDF to {len(images)} page(s)")
                        return images
                    else:
                        logger.error("PDF conversion returned no images")
                        return []
                except ImportError:
                    logger.error("pdf2image not installed. Cannot process PDFs.")
                    return []
                except Exception as e:
                    logger.error(f"PDF conversion failed: {e}")
                    # Try to open as image anyway
                    try:
                        image = Image.open(BytesIO(response.content))
                        logger.info("Opened as image instead")
                        return [image]
                    except:
                        return []

            # Handle Images (single page) - try multiple methods
            try:
                image = Image.open(BytesIO(response.content))
                logger.info(f"Image downloaded successfully. Size: {image.size}, Mode: {image.mode}")
                return [image]
            except Exception as e:
                logger.error(f"Failed to open as image: {e}")
                # Last resort: try to save and reopen
                try:
                    import tempfile
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                        tmp.write(response.content)
                        tmp_path = tmp.name
                    image = Image.open(tmp_path)
                    import os
                    os.unlink(tmp_path)
                    return [image]
                except:
                    return []
            
        except requests.RequestException as e:
            logger.error(f"Failed to download document: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to process document: {e}")
            return []
    
    @staticmethod
    def preprocess_image(image: Image.Image, max_size: tuple = (2048, 2048)) -> Image.Image:
        """
        Preprocess image for better OCR results
        
        Args:
            image: PIL Image object
            max_size: Maximum dimensions (width, height)
            
        Returns:
            Preprocessed PIL Image
        """
        try:
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize if too large
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                logger.info(f"Resizing image from {image.size} to fit {max_size}")
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            return image
            
        except Exception as e:
            logger.error(f"Failed to preprocess image: {e}")
            return image
    
    @staticmethod
    def image_to_bytes(image: Image.Image, format: str = "PNG") -> bytes:
        """
        Convert PIL Image to bytes
        
        Args:
            image: PIL Image object
            format: Image format (PNG, JPEG, etc.)
            
        Returns:
            Image as bytes
        """
        buffer = BytesIO()
        image.save(buffer, format=format)
        return buffer.getvalue()
