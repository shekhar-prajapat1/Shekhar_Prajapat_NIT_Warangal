import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration"""
    
    # Google Gemini API Key
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    
    # Model configuration
    GEMINI_MODEL = "gemini-2.0-flash"
    
    # Image processing settings
    MAX_IMAGE_SIZE = (2048, 2048)  # Max dimensions for processing
    
    # API settings
    API_TITLE = "Bill Data Extraction API"
    API_VERSION = "1.0.0"
    API_DESCRIPTION = "Extract line item details from bill/invoice images"
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY not found in environment variables. "
                "Please set it in .env file or environment."
            )

config = Config()
