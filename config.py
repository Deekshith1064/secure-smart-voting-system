import os

class Config:
    SECRET_KEY = "supersecretkey123"

    DATABASE = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        "database.db"
    )

    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD = "admin123"