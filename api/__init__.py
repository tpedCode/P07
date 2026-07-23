"""
Permet à Python de considérer le dossier 'api' comme un package Python.

Cela rend possible des imports comme :
from api.api_home_credit_scoring import app

Utilisé notamment par Pytest pour charger l'application FastAPI.
"""