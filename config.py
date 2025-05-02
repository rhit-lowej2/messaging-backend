# config.py
# This file contains configuration variables for the application.
import os


class Config:
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")