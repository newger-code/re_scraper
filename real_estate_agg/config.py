import os
from dotenv import load_dotenv

# Load environment variables from.env file
load_dotenv()

class Settings:
    """
    Manages all application settings and credentials loaded from the environment.
    """
    # Bright Data Credentials
    BRIGHT_DATA_USERNAME = os.getenv("BRIGHT_DATA_USERNAME")
    BRIGHT_DATA_PASSWORD = os.getenv("BRIGHT_DATA_PASSWORD")
    BRIGHT_DATA_HOST = os.getenv("BRIGHT_DATA_HOST")
    BRIGHT_DATA_PORT = int(os.getenv("BRIGHT_DATA_PORT", 33335))

    @property
    def proxy_url(self):
        """Constructs the full proxy URL for Playwright."""
        if self.BRIGHT_DATA_USERNAME and self.BRIGHT_DATA_PASSWORD and self.BRIGHT_DATA_HOST and self.BRIGHT_DATA_PORT:
            return f"http://{self.BRIGHT_DATA_USERNAME}:{self.BRIGHT_DATA_PASSWORD}@{self.BRIGHT_DATA_HOST}:{self.BRIGHT_DATA_PORT}"
        return None

    # Database Configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./real_estate.db")

    # Email Notification Configuration
    EMAIL_HOST = os.getenv("EMAIL_HOST")
    EMAIL_PORT = int(os.getenv("EMAIL_PORT", 465))
    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASS = os.getenv("EMAIL_PASS")
    EMAIL_FROM = os.getenv("EMAIL_FROM")
    EMAIL_TO = os.getenv("EMAIL_TO")

    # Google Generative AI for County Scraping Fallback
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    # Address Normalization Configuration
    # Can be 'usaddress' or 'pypostal'
    NORMALIZER_BACKEND = os.getenv("NORMALIZER_BACKEND", "usaddress")

    # Scraping Configuration
    USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36"
    ]
    REQUEST_TIMEOUT = 30  # seconds
    MAX_RETRIES = 3
    RETRY_DELAY = 5 # seconds

settings = Settings()
