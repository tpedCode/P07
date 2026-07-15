"""
Tests de l'endpoint de prédiction.

Objectif :
- vérifier que l'endpoint /predict fonctionne ;
- vérifier que le modèle est correctement chargé ;
- vérifier que les principales validations métier sont opérationnelles ;
- vérifier le fonctionnement batch.

Ces tests automatisent une partie des scénarios Swagger déjà validés.
"""

from fastapi.testclient import TestClient

from api.api_home_credit_scoring import app


# Création du client HTTP de test.
client = TestClient(app)


def test_predict_nominal():
    """
    Vérifie qu'une prédiction nominale fonctionne correctement.
    Correspond au Test 5 Swagger.
    """

    payload = {
        "requested_by": "pytest",
        "clients": [
            {
                "PAYMENT_RATE": 0.05,
                "EXT_SOURCE_MEAN": 0.60,
                "DAYS_BIRTH": -15000,
                "DAYS_EMPLOYED": -2000,
                "AMT_ANNUITY": 15000
            }
        ]
    }

    response = client.post("/predict", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["n_clients"] == 1

    prediction = data["predictions"][0]

    assert "default_probability" in prediction
    assert "decision" in prediction
    assert "feature_coverage_rate" in prediction
    assert "prediction_quality" in prediction


def test_predict_missing_required_feature():
    """
    Vérifie qu'une variable obligatoire absente provoque une erreur de validation.
    Correspond au Test 6 Swagger.
    """

    payload = {
        "requested_by": "pytest",
        "clients": [
            {
                "PAYMENT_RATE": 0.05,
                "EXT_SOURCE_MEAN": 0.60,
                "DAYS_EMPLOYED": -2000,
                "AMT_ANNUITY": 15000
            }
        ]
    }

    response = client.post("/predict", json=payload)

    assert response.status_code == 422


def test_predict_unknown_feature():
    """
    Vérifie qu'une variable inconnue est rejetée.
    Correspond au Test 9 Swagger.
    """

    payload = {
        "requested_by": "pytest",
        "clients": [
            {
                "PAYMENT_RATE": 0.05,
                "EXT_SOURCE_MEAN": 0.60,
                "DAYS_BIRTH": -15000,
                "DAYS_EMPLOYED": -2000,
                "AMT_ANNUITY": 15000,
                "BONJOUR": 123
            }
        ]
    }

    response = client.post("/predict", json=payload)

    assert response.status_code == 422


def test_predict_multiple_clients():
    """
    Vérifie le fonctionnement batch.
    Correspond au Test 12 Swagger.
    """

    payload = {
        "requested_by": "pytest",
        "clients": [
            {
                "PAYMENT_RATE": 0.05,
                "EXT_SOURCE_MEAN": 0.60,
                "DAYS_BIRTH": -15000,
                "DAYS_EMPLOYED": -2000,
                "AMT_ANNUITY": 15000
            },
            {
                "PAYMENT_RATE": 0.12,
                "EXT_SOURCE_MEAN": 0.30,
                "DAYS_BIRTH": -10000,
                "DAYS_EMPLOYED": -500,
                "AMT_ANNUITY": 25000
            }
        ]
    }

    response = client.post("/predict", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["n_clients"] == 2
    assert len(data["predictions"]) == 2