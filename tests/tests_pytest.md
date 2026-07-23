======================================================================
TESTS PYTEST — API HOME CREDIT SCORING
======================================================================

STATUT GLOBAL
-------------
✅ Test 1 — Endpoint /
✅ Test 2 — Endpoint /health
✅ Test 3 — Prédiction nominale
✅ Test 4 — Variable obligatoire absente
✅ Test 5 — Variable inconnue
✅ Test 6 — Multi-clients

======================================================================
TEST 1 — ENDPOINT /
======================================================================

FICHIER
--------
test_home.py

OBJECTIF
---------
Vérifier que l'API démarre correctement et que l'endpoint
d'accueil retourne les informations principales du modèle.

VERIFICATIONS
--------------
✅ HTTP 200
✅ status = "ok"
✅ model présent
✅ business_threshold présent
✅ n_features présent

RESULTAT
----------
PASSED

CONCLUSION
-----------
✅ Endpoint d'accueil fonctionnel.

======================================================================
TEST 2 — ENDPOINT /health
======================================================================

FICHIER
--------
test_health.py

OBJECTIF
---------
Vérifier que l'API répond correctement via son endpoint de santé.

VERIFICATIONS
--------------
✅ HTTP 200
✅ status = "healthy"

RESULTAT
----------
PASSED

CONCLUSION
-----------
✅ Endpoint santé fonctionnel.

======================================================================
TEST 3 — PREDICTION NOMINALE
======================================================================

FICHIER
--------
test_predict.py

OBJECTIF
---------
Vérifier qu'une prédiction standard est réalisée correctement.

VERIFICATIONS
--------------
✅ HTTP 200
✅ n_clients = 1
✅ default_probability présente
✅ decision présente
✅ feature_coverage_rate présent
✅ prediction_quality présent

RESULTAT
----------
PASSED

CONCLUSION
-----------
✅ Le modèle est correctement chargé.
✅ La prédiction est correctement exécutée.

======================================================================
TEST 4 — VARIABLE OBLIGATOIRE ABSENTE
======================================================================

FICHIER
--------
test_predict.py

OBJECTIF
---------
Vérifier qu'une requête incomplète est rejetée.

VERIFICATIONS
--------------
✅ HTTP 422

RESULTAT
----------
PASSED

CONCLUSION
-----------
✅ Validation des variables obligatoires fonctionnelle.

======================================================================
TEST 5 — VARIABLE INCONNUE
======================================================================

FICHIER
--------
test_predict.py

OBJECTIF
---------
Vérifier qu'une variable non connue du modèle est rejetée.

VERIFICATIONS
--------------
✅ HTTP 422

RESULTAT
----------
PASSED

CONCLUSION
-----------
✅ Détection des variables inconnues fonctionnelle.

======================================================================
TEST 6 — MULTI-CLIENTS
======================================================================

FICHIER
--------
test_predict.py

OBJECTIF
---------
Vérifier le fonctionnement batch de l'API.

VERIFICATIONS
--------------
✅ HTTP 200
✅ n_clients = 2
✅ 2 prédictions retournées

RESULTAT
----------
PASSED

CONCLUSION
-----------
✅ Fonctionnement multi-clients validé.

======================================================================
EXECUTION GLOBALE
======================================================================

COMMANDE
---------
pytest -v

RESULTAT OBSERVE
-----------------
tests/test_health.py::test_health_returns_healthy PASSED
tests/test_home.py::test_home_returns_status_ok PASSED
tests/test_predict.py::test_predict_nominal PASSED
tests/test_predict.py::test_predict_missing_required_feature PASSED
tests/test_predict.py::test_predict_unknown_feature PASSED
tests/test_predict.py::test_predict_multiple_clients PASSED
6 passed

======================================================================
BILAN FINAL
======================================================================

✅ Endpoint / validé
✅ Endpoint /health validé
✅ Endpoint /predict validé
✅ Validation des variables obligatoires validée
✅ Validation des variables inconnues validée
✅ Fonctionnement multi-clients validé
✅ Chargement du modèle validé
✅ Chargement du seuil métier validé
✅ Campagne Pytest terminée

======================================================================
ROLE DANS LE CI/CD
======================================================================

Ces tests ont vocation à être exécutés automatiquement
par GitHub Actions à chaque push.

Pipeline cible :

Push Git
    ↓
Installation des dépendances
    ↓
Exécution de Pytest
    ↓
Validation ou échec du build