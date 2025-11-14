import os

# Secret key for Flask session management (Use a secure key in production)
SECRET_KEY = os.getenv("SECRET_KEY", "4f3b2e9a7c8d6e1f5a0b3d2c9e4f8a7b")


# MongoDB Connection URI 
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/chatbot_db")
