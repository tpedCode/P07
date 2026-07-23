"""
Tests de l'endpoint d'accueil.

Objectif :
- vérifier que l'API démarre correctement ;
- vérifier que l'endpoint "/" répond ;
- vérifier que les informations principales du modèle sont disponibles.

Ce test automatise le scénario Swagger :

GET /
-> HTTP 200
-> status = "ok"
"""

# Client HTTP de test fourni par FastAPI.
# Il permet d'appeler les endpoints sans lancer Uvicorn.
from fastapi.testclient import TestClient

# Import de l'application FastAPI.
# C'est exactement la même application utilisée en local et sur Render.
from api.api_home_credit_scoring import app

# Création du client de test.
client = TestClient(app)


def test_home_returns_status_ok():
    """
    Vérifie le comportement nominal de l'endpoint "/".
    """

    # Appel HTTP GET vers l'endpoint d'accueil.
    response = client.get("/")

    # Vérifie que l'appel s'est bien déroulé.
    assert response.status_code == 200

    # Conversion de la réponse JSON en dictionnaire Python.
    data = response.json()

    # Vérifie que l'API indique être opérationnelle.
    assert data["status"] == "ok"

    # Vérifie la présence des informations principales retournées par l'endpoint.
    assert "model" in data
    assert "business_threshold" in data
    assert "n_features" in data