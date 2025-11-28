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
        Download image from URL
        
        Args:
            url: URL of the image to download
            
        Returns:
            PIL Image object or None if download fails
        """
        try:
            logger.info(f"Downloading image from: {url}")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Open image from bytes
            image = Image.open(BytesIO(response.content))
            logger.info(f"Image downloaded successfully. Size: {image.size}, Mode: {image.mode}")
            
            return image
            
        except requests.RequestException as e:
            logger.error(f"Failed to download image: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to process image: {e}")
            return None
    
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
