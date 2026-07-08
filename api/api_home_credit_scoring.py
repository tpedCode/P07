# ==================================================
# API FASTAPI - HOME CREDIT SCORING
# ==================================================

from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException


# ==================================================
# CHEMINS DES ARTEFACTS
# ==================================================

# Le fichier actuel est dans : P07/api/api_home_credit_scoring.py
# parents[1] permet de remonter à la racine du projet : P07/
BASE_DIR = Path(__file__).resolve().parents[1]

# Artefacts produits par le notebook de modélisation
MODEL_PATH = BASE_DIR / "models" / "best_model.pkl"
FEATURES_PATH = BASE_DIR / "models" / "feature_names.pkl"
THRESHOLD_PATH = BASE_DIR / "models" / "threshold.pkl"


# ==================================================
# CHARGEMENT DES ARTEFACTS DU MODELE
# ==================================================

try:
    # Modèle retenu lors de la phase de modélisation
    model = joblib.load(MODEL_PATH)

    # Liste des variables utilisées pendant l'entraînement
    feature_names = joblib.load(FEATURES_PATH)

    # Seuil métier optimisé
    threshold = float(joblib.load(THRESHOLD_PATH))

except Exception as error:
    raise RuntimeError(
        f"Erreur lors du chargement des artefacts du modèle : {error}"
    )


# ==================================================
# INITIALISATION DE L'API
# ==================================================

app = FastAPI(
    title="Home Credit Scoring API",
    description=(
        "API de scoring crédit permettant de calculer la probabilité "
        "de défaut d'un client et de retourner une décision métier."
    ),
    version="1.0.0"
)


# ==================================================
# ENDPOINT D'ACCUEIL
# ==================================================

@app.get("/")
def home():
    """
    Vérifie que l'API est disponible.

    Ce endpoint permet aussi de contrôler rapidement que :
    - le modèle est bien chargé ;
    - les variables sont disponibles ;
    - le seuil métier est récupéré.
    """

    return {
        "status": "ok",
        "model": model.__class__.__name__,
        "n_features": len(feature_names),
        "business_threshold": round(threshold, 6)
    }


# ==================================================
# FONCTION DE PREDICTION
# ==================================================

def predict_client(client_data: dict):
    """
    Calcule la probabilité de défaut d'un client
    et applique le seuil métier optimisé.

    Parameters
    ----------
    client_data : dict
        Données du client envoyées à l'API.

    Returns
    -------
    dict
        Probabilité de défaut, seuil métier et décision finale.
    """

    # Conversion du JSON reçu en DataFrame
    X = pd.DataFrame([client_data])

    # Alignement avec les colonnes utilisées à l'entraînement.
    # Si une variable est absente de la requête, elle est créée avec 0.
    X = X.reindex(
        columns=feature_names,
        fill_value=0
    )

    # Calcul de la probabilité de défaut.
    # La classe 1 correspond au défaut de paiement.
    default_probability = float(
        model.predict_proba(X)[0, 1]
    )

    # Application du seuil métier.
    # Si la probabilité est supérieure ou égale au seuil,
    # la demande de crédit est refusée.
    decision = (
        "REFUSED"
        if default_probability >= threshold
        else "ACCEPTED"
    )

    return {
        "default_probability": round(default_probability, 6),
        "business_threshold": round(threshold, 6),
        "decision": decision
    }


# ==================================================
# ENDPOINT DE PREDICTION
# ==================================================

@app.post("/predict")
def predict(client_data: dict):
    """
    Reçoit les données d'un client au format JSON.

    Retourne :
    - la probabilité de défaut ;
    - le seuil métier utilisé ;
    - la décision ACCEPTED ou REFUSED.
    """

    try:
        return predict_client(client_data)

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la prédiction : {error}"
        )