# Home Credit Scoring

## Présentation du projet

Projet réalisé dans le cadre de la formation **Data Scientist OpenClassrooms** pour la société fictive **« Prêt à Dépenser »**.

L'objectif est de développer un outil de **scoring crédit** permettant d'estimer la probabilité de défaut d'un client et de fournir une décision d'aide à l'octroi du crédit.

Le projet couvre le cycle de vie complet du modèle :

- préparation et feature engineering des données ;
- modélisation et optimisation ;
- explicabilité des prédictions ;
- tracking des expérimentations avec MLflow ;
- gestion du modèle avec le Model Registry ;
- déploiement du modèle sous forme d'API ;
- tests automatisés avec Pytest et GitHub Actions ;
- détection du data drift avec Evidently.

---

## Modèle

Le modèle final retenu est un **LightGBM**.

La sélection du modèle repose notamment sur :

- la validation croisée ;
- l'optimisation des hyperparamètres ;
- l'optimisation du seuil de décision selon le coût métier.

Les principaux artefacts utilisés par l'API sont :

best_model.pkl
threshold.pkl
feature_names.pkl

L'explicabilité du modèle est étudiée à l'aide de :

* Feature Importance globale ;
* SHAP global ;
* SHAP local.

---

## Architecture du projet

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
│   ├── test_health.py
│   ├── test_home.py
│   └── test_predict.py
│
├── documentation/
│   ├── tests_swagger_api.md
│   ├── tests_render.md
│   ├── tests_pytest.md
│   └── tests_github_actions.md
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── requirements.txt
│
└── README.md

### Principaux dossiers

| Dossier              | Description                               |
| -------------------- | ----------------------------------------- |
| `api/`               | Code de l'API FastAPI                     |
| `models/`            | Modèle et artefacts utilisés par l'API    |
| `notebooks/`         | Code de modélisation et d'analyse         |
| `tests/`             | Tests automatisés avec Pytest             |
| `documentation/`     | Documentation et comptes rendus des tests |
| `.github/workflows/` | Configuration du pipeline GitHub Actions  |

---

## MLOps

Le projet met en œuvre plusieurs composants MLOps :

* **MLflow** : tracking des expérimentations ;
* **MLflow UI** : visualisation des résultats ;
* **MLflow Model Registry** : gestion centralisée des modèles ;
* **MLflow Serving** : test du serving du modèle ;
* **Git / GitHub** : versionnement du code ;
* **GitHub Actions** : intégration continue et exécution automatique des tests ;
* **Pytest** : tests automatisés de l'API ;
* **Evidently** : analyse du data drift.

---

## API

L'API est développée avec **FastAPI** et permet de :

* calculer une probabilité de défaut ;
* appliquer le seuil métier optimisé ;
* retourner une décision `ACCEPTED` ou `REFUSED` ;
* gérer plusieurs clients dans une même requête ;
* contrôler les données d'entrée.

Endpoints principaux :

GET  /
GET  /health
POST /predict

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

## Lancement de l'API en local

Depuis la racine du projet :

```bash
uvicorn api.api_home_credit_scoring:app --reload
```

Documentation Swagger :

```text
http://127.0.0.1:8000/docs
```

---

## Tests

Les tests automatisés sont exécutés avec Pytest :

```bash
pytest -v
```

Le workflow GitHub Actions exécute automatiquement les tests lors des événements configurés sur le dépôt.

---

## API déployée

L'API est déployée sur **Render**.

URL :

```text
https://p07-home-credit-scoring.onrender.com
```

Swagger :

```text
https://p07-home-credit-scoring.onrender.com/docs
```

---

## Auteur

Projet réalisé dans le cadre de la formation **Data Scientist OpenClassrooms**.