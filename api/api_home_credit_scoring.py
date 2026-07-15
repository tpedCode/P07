# ==================================================
# API FASTAPI - HOME CREDIT SCORING
# ==================================================

"""
Objectif :
- exposer un modèle de scoring crédit sous forme d'API ;
- recevoir les données d'un ou plusieurs clients ;
- contrôler la qualité minimale des données avant prédiction ;
- calculer une probabilité de défaut ;
- appliquer le seuil métier optimisé ;
- retourner une décision exploitable par les équipes métier.

Postulat de fonctionnement :
- l'API reçoit des données déjà préparées pour le modèle ;
- les variables issues du feature engineering sont supposées être déjà présentes dans les données envoyées ;
- l'API réalise uniquement la validation des données, la préparation finale des colonnes attendues par le modèle et la prédiction ;
- la reconstruction complète du feature engineering du notebook n'est pas réalisée dans l'API car elle nécessite l'accès à plusieurs sources de données ;
- les sources nécessaires au feature engineering complet incluent notamment Application, Bureau, Previous Application et Installments Payments.

Choix métiers :
- refuser une demande lorsque la probabilité de défaut est supérieure ou égale au seuil métier ;
- rendre obligatoires uniquement les variables très importantes et directement exploitables ;
- distinguer les variables obligatoires, fortement recommandées et optionnelles ;
- autoriser certaines variables importantes à être absentes, mais informer l'utilisateur ;
- remplacer les variables optionnelles absentes par 0 pour rester compatible avec le modèle ;
- fournir un indicateur de qualité de prédiction basé sur l'importance des variables présentes ;
- ne pas journaliser les données clients complètes pour limiter les risques de confidentialité.

Choix techniques :
- FastAPI expose les endpoints de prédiction ;
- Pydantic valide le format des données reçues ;
- Joblib permet de charger le modèle et les artefacts sauvegardés ;
- Pandas reconstruit les colonnes attendues par le modèle ;
- le modèle utilise predict_proba pour produire une probabilité de défaut ;
- la qualité de prédiction est estimée à partir de la couverture pondérée des variables ;
- les logs enregistrent uniquement des informations minimales sur les requêtes.

Entrée / Sortie :
- entrée : requête JSON contenant une liste de clients ;
- sortie : réponse JSON contenant les probabilités, le seuil métier, les décisions, la qualité des données et les warnings.
"""

from pathlib import Path
from typing import Any

import logging
import joblib
import pandas as pd

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field, field_validator


# ==================================================
# CONFIGURATION DES LOGS
# ==================================================

# Les logs permettent de suivre l'activité minimale de l'API.
# On évite volontairement de stocker les données clients complètes.

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# ==================================================
# CHEMINS DES ARTEFACTS
# ==================================================

# Le fichier actuel est situé dans :
# P07/api/api_home_credit_scoring.py
#
# parents[1] permet de remonter à la racine du projet :
# P07/

BASE_DIR = Path(__file__).resolve().parents[1]

# Artefacts produits par le notebook de modélisation.
# Ils permettent à l'API de fonctionner sans relancer le notebook.

MODEL_PATH = BASE_DIR / "models" / "best_model.pkl"
FEATURES_PATH = BASE_DIR / "models" / "feature_names.pkl"
THRESHOLD_PATH = BASE_DIR / "models" / "threshold.pkl"


# ==================================================
# CHARGEMENT DES ARTEFACTS DU MODELE
# ==================================================

try:
    # Modèle final retenu lors de la phase de modélisation.
    model = joblib.load(MODEL_PATH)

    # Liste exacte des variables utilisées à l'entraînement.
    feature_names = joblib.load(FEATURES_PATH)

    # Seuil métier optimisé (ce seuil remplace le seuil standard 0.5).
    threshold = float(joblib.load(THRESHOLD_PATH))

except Exception as error:
    raise RuntimeError(
        f"Erreur lors du chargement des artefacts du modèle : {error}"
    )


# ==================================================
# CATEGORIES DE VARIABLES
# ==================================================

# Catégorie 1 : variables obligatoires.
#
# Ces variables ont été sélectionnées à partir de la Feature Importance
# Global (FIG) du modèle.
#
# Elles représentent un compromis entre :
# - importance prédictive ;
# - disponibilité métier ;
# - facilité d'obtention lors d'un appel API.
#
# Certaines variables plus importantes dans le modèle n'ont pas été rendues
# obligatoires car elles nécessitent des agrégations complexes ou l'accès à
# des sources de données supplémentaires (historique bureau, crédits passés,
# remboursements, etc.).
#
# Si l'une de ces variables est absente, la requête est refusée.

REQUIRED_FEATURES = [
    "PAYMENT_RATE",
    "EXT_SOURCE_MEAN",
    "DAYS_BIRTH",
    "DAYS_EMPLOYED",
    "AMT_ANNUITY"
]


# Catégorie 2 : variables fortement recommandées.
#
# Ces variables présentent également une forte importance dans le modèle.
#
# Elles améliorent la qualité de la prédiction mais ne sont pas
# systématiquement disponibles dans tous les scénarios métier.
#
# Si elles sont absentes :
# - la prédiction reste possible ;
# - la qualité de complétude pondérée diminue ;
# - un warning est retourné.

RECOMMENDED_FEATURES = [
    "EXT_SOURCE_1",
    "EXT_SOURCE_2",
    "EXT_SOURCE_3",
    "DAYS_ID_PUBLISH",
    "DAYS_REGISTRATION",
    "DAYS_LAST_PHONE_CHANGE"
]


# Catégorie 3 : variables optionnelles.
#
# Toutes les autres variables attendues par le modèle sont considérées comme
# optionnelles.
#
# Cela inclut notamment des variables issues d'agrégations sur :
# - l'historique de crédit externe (BURO_*) ;
# - les demandes de crédit précédentes (PREV_*) ;
# - les historiques de remboursement (INSTAL_*).
#
# Si elles sont absentes, elles sont remplacées par 0 lors de la
# reconstruction du DataFrame de prédiction.

OPTIONAL_FEATURES = [
    feature
    for feature in feature_names
    if feature not in REQUIRED_FEATURES
    and feature not in RECOMMENDED_FEATURES
]


# ==================================================
# IMPORTANCES GLOBALES DU MODELE
# ==================================================

# Les importances globales permettent de calculer une complétude pondérée.
#
# L'objectif n'est pas seulement de compter le nombre de variables présentes, mais de mesurer si les variables les plus utiles au modèle sont fournies.

if (
    hasattr(model, "feature_importances_")
    and len(model.feature_importances_) == len(feature_names)
):
    feature_importance_map = dict(
        zip(
            feature_names,
            model.feature_importances_
        )
    )
else:
    # Fallback de sécurité si le modèle ne fournit pas d'importances.
    # Dans ce cas, chaque variable reçoit le même poids.
    feature_importance_map = {
        feature: 1
        for feature in feature_names
    }

total_feature_importance = sum(feature_importance_map.values())

if total_feature_importance == 0:
    total_feature_importance = len(feature_names)


# ==================================================
# SCHEMA D'UN CLIENT
# ==================================================

class ClientData(BaseModel):
    """
    Objectif :
    - définir le format minimal attendu pour un client ;
    - garantir que les variables obligatoires sont présentes ;
    - contrôler les types avant prédiction.

    Choix métiers :
    - les variables obligatoires sont issues de l'analyse globale des importances ;
    - seules les variables importantes et facilement exploitables sont rendues obligatoires ;
    - les variables fortement recommandées améliorent la qualité de la prédiction, mais ne bloquent pas la requête ;
    - les variables optionnelles permettent d'enrichir la prédiction si elles sont disponibles ;
    - l'API est positionnée après la phase de feature engineering ;
    - les variables dérivées comme PAYMENT_RATE ou EXT_SOURCE_MEAN sont supposées déjà calculées en amont.

    Choix techniques :
    - Pydantic valide automatiquement les champs obligatoires ;
    - extra="allow" autorise l'envoi des variables recommandées et optionnelles en plus des variables obligatoires ;
    - les variables reçues sont ensuite contrôlées par rapport aux variables connues du modèle ;
    - les booléens sont refusés car True/False ne sont pas des valeurs métier numériques valides.

    Entrée / Sortie :
    - entrée : données JSON d'un client ;
    - sortie : objet ClientData validé ou erreur 422 en cas de donnée invalide.
    """

    # Autorise la transmission des variables recommandées et optionnelles
    # en plus des variables obligatoires.
    #
    # Les variables reçues seront ensuite vérifiées par rapport aux
    # features du modèle afin de rejeter toute variable inconnue.
    model_config = ConfigDict(extra="allow")

    PAYMENT_RATE: float = Field(
        ...,
        description="Ratio de paiement déjà calculé pendant le feature engineering."
    )

    EXT_SOURCE_MEAN: float = Field(
        ...,
        description="Moyenne des scores externes déjà calculée pendant le feature engineering."
    )

    DAYS_BIRTH: float = Field(
        ...,
        description="Âge du client encodé selon la convention du dataset Home Credit."
    )

    DAYS_EMPLOYED: float = Field(
        ...,
        description="Ancienneté professionnelle encodée selon la convention du dataset Home Credit."
    )

    AMT_ANNUITY: float = Field(
        ...,
        ge=0,
        description="Montant de l'annuité. Doit être positif ou nul."
    )

    @field_validator(
        "PAYMENT_RATE",
        "EXT_SOURCE_MEAN",
        "DAYS_BIRTH",
        "DAYS_EMPLOYED",
        "AMT_ANNUITY",
        mode="before"
    )
    @classmethod
    def validate_numeric_required_features(cls, value: Any):
        """
        Objectif :
        - vérifier que les variables obligatoires sont bien numériques.

        Choix métiers :
        - empêcher une décision de crédit basée sur une valeur textuelle ou booléenne ;
        - garantir un minimum de cohérence avant l'appel au modèle.

        Choix techniques :
        - contrôle réalisé avant conversion Pydantic ;
        - rejet des booléens ;
        - rejet des chaînes de caractères ;
        - seules les valeurs numériques sont autorisées.

        Entrée / Sortie :
        - entrée : valeur reçue pour une variable obligatoire ;
        - sortie : valeur validée ou erreur de validation.
        """

        if isinstance(value, bool):
            raise ValueError("La valeur doit être numérique, pas booléenne.")

        if not isinstance(value, (int, float)):
            raise ValueError("La valeur doit être numérique.")

        return value


# ==================================================
# SCHEMA DE REQUETE
# ==================================================

class PredictionRequest(BaseModel):
    """
    Objectif :
    - définir le contrat d'entrée de l'endpoint de prédiction ;
    - permettre de scorer un ou plusieurs clients avec une seule route.

    Choix métiers :
    - conserver un format unique pour les prédictions unitaires et multiples ;
    - identifier de manière déclarative la personne ou le système demandeur ;
    - faciliter la traçabilité sans mettre en place d'authentification complète ;
    - le système appelant est responsable de fournir des données déjà préparées ;
    - l'API n'effectue pas la construction des variables issues du feature engineering ;
    - l'API est dédiée à l'étape de scoring et non à la préparation des données.

    Choix techniques :
    - la requête contient toujours une liste de clients ;
    - min_length=1 empêche les requêtes sans client ;
    - requested_by reste optionnel et vaut "anonymous" par défaut.

    Entrée / Sortie :
    - entrée : requête JSON contenant requested_by et clients ;
    - sortie : objet PredictionRequest validé ou erreur 422 en cas de format invalide.
    """

    requested_by: str = Field(
        default="anonymous",
        description=(
            "Identifiant déclaratif de la personne ou du système ayant demandé la prédiction."
        )
    )

    clients: list[ClientData] = Field(
        ...,
        min_length=1,
        description="Liste des clients à scorer."
    )


# ==================================================
# INITIALISATION DE L'API
# ==================================================

app = FastAPI(
    title="Home Credit Scoring API",
    description=(
        "API de scoring crédit permettant de calculer la probabilité de défaut d'un ou "
        "plusieurs clients et de retourner une décision métier basée sur un seuil optimisé."
    ),
    version="1.2.0"
)


# ==================================================
# ENDPOINT D'ACCUEIL
# ==================================================

@app.get("/")
def home():
    """
    Objectif :
    - vérifier que l'API est disponible ;
    - afficher les informations principales du modèle chargé.

    Choix métiers :
    - rendre visible le seuil métier utilisé par l'API ;
    - vérifier rapidement que l'API utilise bien le modèle attendu.

    Choix techniques :
    - endpoint simple utilisé pour le contrôle manuel ou les tests ;
    - aucune donnée client n'est nécessaire.

    Entrée / Sortie :
    - entrée : aucune ;
    - sortie : statut de l'API, nom du modèle, nombre de variables et seuil métier.
    """

    return {
        "status": "ok",
        "model": model.__class__.__name__,
        "n_features": len(feature_names),
        "n_required_features": len(REQUIRED_FEATURES),
        "n_recommended_features": len(RECOMMENDED_FEATURES),
        "business_threshold": round(threshold, 6)
    }


# ==================================================
# ENDPOINT DE SANTE
# ==================================================

@app.get("/health")
def health():
    """
    Objectif :
    - fournir un point de contrôle simple pour vérifier que l'API répond.

    Choix métiers :
    - aucun traitement métier n'est effectué dans ce endpoint.

    Choix techniques :
    - endpoint principalement utile dans un contexte de déploiement et de supervision ;
    - dans le cadre de ce projet, il complète l'endpoint d'accueil en séparant :
        - les informations détaillées sur le modèle (/)
        - le simple contrôle de disponibilité de l'API (/health) ;
    - réponse volontairement minimale afin de limiter le coût des vérifications automatiques.

    Entrée / Sortie :
    - entrée : aucune ;
    - sortie : statut de santé de l'API.
    """

    return {
        "status": "healthy"
    }


# ==================================================
# VALIDATION DES VARIABLES OPTIONNELLES
# ==================================================

def validate_optional_features(client_data: dict):
    """
    Objectif :
    - vérifier la cohérence des variables recommandées et optionnelles envoyées à l'API ;
    - s'assurer que seules les variables connues du modèle sont transmises.

    Choix métiers :
    - une variable utilisée par le modèle doit rester exploitable ;
    - une valeur textuelle ou booléenne ne doit pas être transmise au modèle ;
    - toute variable inconnue du modèle est considérée comme une erreur de saisie ou de mapping ;
    - la prédiction est refusée lorsqu'une variable inconnue est détectée.

    Choix techniques :
    - les variables reçues sont comparées à feature_names ;
    - une erreur est levée si une variable inconnue est présente ;
    - les variables connues doivent être numériques ;
    - une erreur est levée avant predict_proba en cas de donnée invalide.

    Entrée / Sortie :
    - entrée : dictionnaire des données d'un client ;
    - sortie : aucune sortie directe ;
    - exception :
        - ValueError si une variable inconnue du modèle est détectée ;
        - ValueError si une variable connue du modèle n'est pas numérique.
    """

    # Vérifie qu'aucune variable inconnue du modèle n'est fournie.
    unknown_features = [
        key
        for key in client_data.keys()
        if key not in feature_names
    ]

    if unknown_features:
        raise ValueError(
            f"Variables inconnues du modèle : {unknown_features}"
        )

    # Vérifie que les variables connues du modèle sont numériques.
    for key, value in client_data.items():

        if isinstance(value, bool):
            raise ValueError(
                f"La variable '{key}' doit être numérique, pas booléenne."
            )

        if not isinstance(value, (int, float)):
            raise ValueError(
                f"La variable '{key}' doit être numérique."
            )


# ==================================================
# PREPARATION DES DONNEES POUR LE MODELE
# ==================================================

def prepare_client_features(client_data: dict):
    """
    Objectif :
    - reconstruire les données du client au format exact attendu par le modèle ;
    - compléter les variables optionnelles absentes ;
    - calculer les variables absentes par catégorie.

    Choix métiers :
    - le feature engineering est considéré comme déjà réalisé avant l'appel à l'API ;
    - l'API ne recalcule pas les variables dérivées créées pendant la phase de modélisation ;
    - les variables obligatoires sont déjà validées par Pydantic ;
    - les variables recommandées absentes n'empêchent pas la prédiction, mais diminuent la qualité attendue ;
    - les variables optionnelles absentes ne bloquent pas la prédiction ;
    - les absences sont communiquées dans la réponse.

    Choix techniques :
    - seules les variables connues du modèle sont conservées ;
    - l'ordre des colonnes est corrigé avec feature_names ;
    - les colonnes absentes sont créées avec la valeur 0 ;
    - le résultat est un DataFrame compatible avec predict_proba.

    Entrée / Sortie :
    - entrée : dictionnaire des données d'un client ;
    - sortie :
        - X : DataFrame contenant les colonnes attendues par le modèle ;
        - known_features : variables connues du modèle et fournies par le client ;
        - missing_recommended_features : variables recommandées absentes ;
        - n_missing_optional_features : nombre de variables optionnelles absentes.
    """

    # Conservation uniquement des variables connues par le modèle.
    known_features = {
        key: value
        for key, value in client_data.items()
        if key in feature_names
    }

    # Variables recommandées absentes.
    missing_recommended_features = [
        feature
        for feature in RECOMMENDED_FEATURES
        if feature not in known_features
    ]

    # Variables optionnelles absentes.
    missing_optional_features = [
        feature
        for feature in OPTIONAL_FEATURES
        if feature not in known_features
    ]

    n_missing_optional_features = len(missing_optional_features)

    # Création d'une ligne de données pour le client.
    X = pd.DataFrame([known_features])

    # Alignement strict avec les colonnes utilisées pendant l'entraînement.
    X = X.reindex(
        columns=feature_names,
        fill_value=0
    )

    return (
        X,
        known_features,
        missing_recommended_features,
        n_missing_optional_features
    )


# ==================================================
# QUALITE DE COMPLETUDE PONDEREE
# ==================================================

def compute_feature_coverage(known_features: dict):
    """
    Objectif :
    - estimer la qualité des données reçues avant interprétation de la prédiction ;
    - mesurer la part d'importance du modèle couverte par les variables fournies.

    Choix métiers :
    - une prédiction basée sur les variables les plus importantes est plus fiable ;
    - le nombre brut de variables manquantes est moins pertinent que leur importance ;
    - l'API retourne donc un indicateur de qualité exploitable par un utilisateur métier.

    Choix techniques :
    - les importances globales du modèle sont utilisées comme pondération ;
    - la couverture est calculée comme :
      importance des variables présentes / importance totale du modèle ;
    - la qualité est catégorisée en HIGH, MEDIUM ou LOW.

    Entrée / Sortie :
    - entrée : dictionnaire des variables connues du modèle et fournies par le client ;
    - sortie :
        - feature_coverage_rate : pourcentage d'importance couverte ;
        - prediction_quality : niveau de qualité estimé.
    """

    covered_importance = sum(
        feature_importance_map.get(feature, 0)
        for feature in known_features
    )

    feature_coverage_rate = (
        covered_importance / total_feature_importance
    ) * 100

    if feature_coverage_rate >= 80:
        prediction_quality = "HIGH"
    elif feature_coverage_rate >= 50:
        prediction_quality = "MEDIUM"
    else:
        prediction_quality = "LOW"

    return round(feature_coverage_rate, 2), prediction_quality


# ==================================================
# WARNING METIER
# ==================================================

def build_warning(
    prediction_quality: str,
    feature_coverage_rate: float,
    missing_recommended_features: list[str],
    n_missing_optional_features: int
):
    """
    Objectif :
    - construire un message explicite sur la qualité des données utilisées ;
    - fournir des indicateurs permettant d'interpréter le niveau de confiance
      associé à la prédiction.

    Choix métiers :
    - distinguer l'absence de variables recommandées de l'absence de variables optionnelles ;
    - informer l'utilisateur lorsque la prédiction doit être interprétée avec prudence ;
    - éviter de laisser croire qu'une prédiction très incomplète a la même fiabilité
      qu'une prédiction basée sur un ensemble complet de données ;
    - rendre visibles les principaux indicateurs de qualité utilisés par l'API.

    Choix techniques :
    - le message dépend du niveau de complétude pondérée calculé ;
    - la complétude est calculée à partir des importances globales du modèle ;
    - les seuils utilisés sont :
        - LOW    : complétude < 50 %
        - MEDIUM : 50 % ≤ complétude < 80 %
        - HIGH   : complétude ≥ 80 %
    - la liste des variables recommandées absentes est retournée explicitement ;
    - le nombre de variables optionnelles absentes est indiqué.

    Entrée / Sortie :
    - entrée :
        - prediction_quality : niveau de qualité (LOW, MEDIUM, HIGH) ;
        - feature_coverage_rate : taux de complétude pondérée (%) ;
        - missing_recommended_features : variables recommandées absentes ;
        - n_missing_optional_features : nombre de variables optionnelles absentes.

    - sortie :
        - chaîne de caractères contenant le warning.
    """

    # Message principal décrivant le niveau de complétude pondérée.
    if prediction_quality == "LOW":

        warning = (
            f"Complétude pondérée : {feature_coverage_rate:.2f}% "
            "(< 50%). "
            "La prédiction repose sur une faible couverture des variables "
            "les plus importantes du modèle et doit être interprétée avec prudence."
        )

    elif prediction_quality == "MEDIUM":

        warning = (
            f"Complétude pondérée : {feature_coverage_rate:.2f}% "
            "(entre 50% et 80%). "
            "La prédiction repose sur une couverture partielle des variables les plus importantes du modèle."
        )

    else:

        warning = (
            f"Complétude pondérée : {feature_coverage_rate:.2f}% "
            "(≥ 80%). "
            "La couverture des variables importantes est jugée satisfaisante."
        )

    # Ajout de la liste des variables recommandées absentes.
    if missing_recommended_features:

        warning += (
            f" Variables fortement recommandées absentes : "
            f"{missing_recommended_features}."
        )

    # Ajout du nombre de variables optionnelles manquantes.
    warning += (
        f" Nombre de variables optionnelles absentes : "
        f"{n_missing_optional_features}."
    )

    return warning


# ==================================================
# PREDICTION POUR UN CLIENT
# ==================================================

def predict_single_client(client: ClientData, client_index: int):
    """
    Objectif :
    - calculer la probabilité de défaut d'un client ;
    - appliquer le seuil métier optimisé ;
    - retourner une décision métier exploitable ;
    - informer sur la qualité des données utilisées pour la prédiction.

    Choix métiers :
    - la décision n'est pas basée sur le seuil standard 0.5 ;
    - la décision utilise le seuil métier optimisé pendant la modélisation ;
    - une probabilité supérieure ou égale au seuil entraîne un refus ;
    - la réponse distingue les variables obligatoires, recommandées et optionnelles ;
    - la qualité de complétude pondérée permet d'interpréter plus justement la prédiction.

    Choix techniques :
    - l'objet Pydantic est transformé en dictionnaire ;
    - les variables fournies sont validées ;
    - les colonnes sont reconstruites dans l'ordre attendu par le modèle ;
    - predict_proba permet de récupérer la probabilité de défaut ;
    - la couverture des variables est calculée avec les importances globales du modèle ;
    - la réponse est directement sérialisable en JSON.

    Entrée / Sortie :
    - entrée :
        - client : objet ClientData validé par Pydantic ;
        - client_index : position du client dans la requête.
    - sortie :
        - dictionnaire contenant client_index, default_probability,
          business_threshold, decision, feature_coverage_rate,
          prediction_quality, missing_recommended_features,
          missing_optional_features et warning.
    """

    # Conversion en dictionnaire pour préparer les données du modèle.
    client_data = client.model_dump()

    # Contrôle des variables connues du modèle.
    validate_optional_features(client_data)

    # Reconstruction du DataFrame compatible avec le modèle entraîné.
    (
        X,
        known_features,
        missing_recommended_features,
        n_missing_optional_features
    ) = prepare_client_features(client_data)

    # Calcul de la complétude pondérée par importance.
    feature_coverage_rate, prediction_quality = compute_feature_coverage(
        known_features
    )

    # Calcul de la probabilité de défaut.
    default_probability = float(
        model.predict_proba(X)[0, 1]
    )

    # Application du seuil métier optimisé.
    decision = (
        "REFUSED"
        if default_probability >= threshold
        else "ACCEPTED"
    )

    # Construction du warning métier.
    warning = build_warning(
        prediction_quality=prediction_quality,
        feature_coverage_rate=feature_coverage_rate,
        missing_recommended_features=missing_recommended_features,
        n_missing_optional_features=n_missing_optional_features
    )

    return {
        "client_index": client_index,
        "default_probability": round(default_probability, 6),
        "business_threshold": round(threshold, 6),
        "decision": decision,
        "feature_coverage_rate": feature_coverage_rate,
        "prediction_quality": prediction_quality,
        "missing_recommended_features": missing_recommended_features,
        "n_missing_optional_features": n_missing_optional_features,
        "warning": warning
    }


# ==================================================
# ENDPOINT DE PREDICTION
# ==================================================

@app.post("/predict")
def predict(request: PredictionRequest):
    """
    Objectif :
    - scorer un ou plusieurs clients via une seule requête ;
    - retourner une prédiction complète pour chaque client.

    Choix métiers :
    - l'API peut traiter un cas individuel ou un lot de clients ;
    - toutes les décisions utilisent le même seuil métier ;
    - la réponse reste explicite pour chaque client ;
    - la qualité de la prédiction est indiquée à partir des variables importantes fournies ;
    - les logs permettent de suivre l'activité sans stocker les données sensibles.

    Choix techniques :
    - Pydantic valide la structure globale de la requête ;
    - chaque client est traité séquentiellement ;
    - les erreurs de validation métier renvoient un statut 422 ;
    - les erreurs inattendues renvoient un statut 500 ;
    - les logs enregistrent le demandeur, le nombre de clients, les décisions et les niveaux de qualité.

    Entrée / Sortie :
    - entrée :
        - request : objet PredictionRequest contenant requested_by et clients.
    - sortie :
        - requested_by ;
        - n_clients ;
        - predictions ;
        - pour chaque client : probabilité, seuil, décision, qualité et warning.
    """

    try:
        predictions = []

        # Les clients sont traités un par un afin de conserver une réponse détaillée pour chaque client.
        for index, client in enumerate(request.clients):
            prediction = predict_single_client(
                client=client,
                client_index=index
            )
            predictions.append(prediction)

        # Extraction des décisions et qualités pour les logs.
        decisions = [
            prediction["decision"]
            for prediction in predictions
        ]

        qualities = [
            prediction["prediction_quality"]
            for prediction in predictions
        ]

        # Log minimal, sans données clients complètes.
        logger.info(
            "requested_by=%s | endpoint=/predict | n_clients=%s | decisions=%s | qualities=%s",
            request.requested_by,
            len(request.clients),
            decisions,
            qualities
        )

        return {
            "requested_by": request.requested_by,
            "n_clients": len(request.clients),
            "predictions": predictions
        }

    except ValueError as error:
        # Erreur liée à une donnée invalide envoyée à l'API.
        raise HTTPException(
            status_code=422,
            detail=str(error)
        )

    except Exception as error:
        # Erreur inattendue pendant la prédiction.
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la prédiction : {error}"
        )