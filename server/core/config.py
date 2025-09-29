import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MongoDB
MONGO_URI = os.getenv("MONGO_URI")

# Google OAuth
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

# JWT
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
