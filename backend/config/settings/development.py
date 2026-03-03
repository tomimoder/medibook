from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# CORS: permite que React en localhost hable con la API
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',  # Vite (React)
    'http://localhost:3000',
]

# Emails en consola durante desarrollo (no envía emails reales)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'