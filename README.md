# Home Credit Scoring

## Contexte métier

La société fictive "Prêt à Dépenser" souhaite développer un outil d’aide à la décision pour l’octroi de crédits.

L’objectif est d’estimer le risque de défaut de paiement d’un client à partir de ses caractéristiques et de fournir une décision métier exploitable.

Ce projet couvre l'ensemble du cycle de vie d'un modèle de Machine Learning :

- préparation des données ;
- feature engineering ;
- modélisation ;
- explicabilité ;
- MLOps ;
- déploiement sous forme d'API ;
- surveillance du data drift.

---

## Objectif du projet

Développer une solution de scoring crédit capable de :

- prédire le risque de défaut d'un client ;
- optimiser la prise de décision grâce à un seuil métier ;
- fournir une décision ACCEPTED ou REFUSED ;
- expliquer les prédictions ;
- exposer le modèle via une API ;
- suivre les expérimentations avec MLflow ;
- surveiller l'évolution des données avec Evidently.

---

## Structure du projet

```text
P07/
│
├── api/
│   └── api_home_credit_scoring.py
│
├── models/
│   ├── best_model.pkl
│   ├── threshold.pkl
│   └── feature_names.pkl
│
├── notebooks/
│   └── notebook_modelisation.ipynb
│
├── tests/
│
├── documentation/
│   └── tests_swagger_api.md
│
├── requirements.txt
│
└── README.md
```

---

## Modèle retenu

Modèle final :

```text
LightGBM
```

Travail réalisé :

- validation croisée ;
- optimisation des hyperparamètres ;
- optimisation du seuil métier ;
- sélection du meilleur modèle.

Artefacts sauvegardés :

```text
best_model.pkl
threshold.pkl
feature_names.pkl
```

---

## Explicabilité

Les analyses suivantes ont été réalisées :

- Feature Importance globale ;
- SHAP global ;
- SHAP local.

---

## MLOps

Le projet intègre :

- MLflow Tracking ;
- MLflow UI ;
- Model Registry ;
- Serving du modèle.

---

## API de prédiction

L'API expose les endpoints suivants.

### GET /

Retourne :

- le statut de l’API ;
- le modèle chargé ;
- le seuil métier ;
- le nombre de variables attendues.

### GET /health

Permet de vérifier que l’API est disponible.

### POST /predict

Retourne :

- la probabilité de défaut ;
- la décision métier ;
- les indicateurs de qualité de prédiction.

---

## Catégories de variables

L’API distingue trois catégories de variables.

### Variables obligatoires

Ces variables doivent être présentes dans chaque requête.

```text
PAYMENT_RATE
EXT_SOURCE_MEAN
DAYS_BIRTH
DAYS_EMPLOYED
AMT_ANNUITY
```

### Variables fortement recommandées

Ces variables améliorent la qualité de la prédiction mais ne bloquent pas l’API lorsqu’elles sont absentes.

### Variables optionnelles

Toutes les autres variables connues du modèle.

Elles sont utilisées lorsqu’elles sont fournies.

---

## Indicateurs métier

L'API fournit plusieurs indicateurs destinés à faciliter l'interprétation de la prédiction.

### feature_coverage_rate

Mesure la part d’importance du modèle couverte par les variables réellement fournies.

### prediction_quality

Niveau de qualité associé à la prédiction :

```text
LOW
MEDIUM
HIGH
```

### warning

Message explicatif destiné à informer l’utilisateur sur la qualité des données utilisées.

---

## Installation

Créer et activer un environnement virtuel :

```bash
python -m venv venv
```

Sous Windows :

```bash
venv\Scripts\activate
```

Installer les dépendances :

```bash
pip install -r requirements.txt
```

---

## Lancement de l'API

Depuis la racine du projet :

```bash
uvicorn api.api_home_credit_scoring:app --reload
```

Documentation Swagger :

```text
http://127.0.0.1:8000/docs
```

---

## Exemple de requête

```json
{
  "requested_by": "test_swagger",
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
```

---

## Validation de l'API

Une campagne complète de tests Swagger a été réalisée :

- démarrage de l’API ;
- endpoint d’accueil ;
- endpoint santé ;
- prédiction nominale ;
- variable obligatoire absente ;
- type invalide ;
- booléen ;
- variable inconnue ;
- variables recommandées ;
- variable optionnelle ;
- multi-clients ;
- liste vide ;
- ancien format de requête.

---

## Déploiement

API déployée sur Render :

```text
À compléter après le déploiement.
```

---

## Auteur

Projet réalisé dans le cadre de la formation Data Scientist OpenClassrooms.