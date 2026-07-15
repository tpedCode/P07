"""
Tests de l'endpoint de santé.

Objectif :
- vérifier que l'API répond ;
- vérifier que le endpoint /health est disponible ;
- vérifier que le statut retourné est correct.

Ce test automatise le scénario Swagger :

GET /health
-> HTTP 200
-> status = "healthy"
"""

from fastapi.testclient import TestClient

from api.api_home_credit_scoring import app


# Création d'un client de test HTTP.
client = TestClient(app)


def test_health_returns_healthy():
    """
    Vérifie que l'endpoint /health répond correctement.
    """

    # Appel HTTP GET vers l'endpoint de santé.
    response = client.get("/health")

    # Vérifie le statut HTTP.
    assert response.status_code == 200

    # Conversion du JSON en dictionnaire Python.
    data = response.json()

    # Vérifie le contenu retourné.
    assert data["status"] == "healthy"