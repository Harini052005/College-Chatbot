import os

# Secret key for Flask session management (Use a secure key in production)
SECRET_KEY = os.getenv("SECRET_KEY", "place_secretkey_ here")


# MongoDB Connection URI 
MONGO_URI = os.getenv("MONGO_URI", "place_mongodb_connection_here")

