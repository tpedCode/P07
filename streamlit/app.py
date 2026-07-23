# ==================================================
# STREAMLIT — TEST DE L'API HOME CREDIT SCORING
# ==================================================

import requests
import streamlit as st


# ==================================================
# CONFIGURATION
# ==================================================

API_URL = "https://p07-home-credit-scoring.onrender.com"

st.set_page_config(
    page_title="Home Credit Scoring — API Test",
    page_icon="💳",
    layout="wide"
)


# ==================================================
# FONCTIONS API
# ==================================================

def api_get(endpoint):
    """Effectue une requête GET vers l'API."""
    response = requests.get(
        f"{API_URL}{endpoint}",
        timeout=60
    )
    response.raise_for_status()
    return response.json()


def api_predict(payload):
    """Envoie une requête de prédiction à l'API."""
    response = requests.post(
        f"{API_URL}/predict",
        json=payload,
        timeout=60
    )
    return response


# ==================================================
# TITRE
# ==================================================

st.title("Home Credit Scoring — API Test")


# ==================================================
# 1. SANTE DE L'API
# ==================================================

st.header("1. Santé de l'API")

try:
    health = api_get("/health")

    if health.get("status") == "healthy":
        st.success("API opérationnelle")
    else:
        st.warning(f"Statut API inattendu : {health}")

except requests.exceptions.Timeout:
    st.warning(
        "L'API met du temps à répondre. "
        "Le service Render est peut-être en sortie de veille."
    )

except requests.exceptions.RequestException as error:
    st.error(f"Impossible de contacter l'API : {error}")


# ==================================================
# 2. INFORMATIONS API ET MODELE
# ==================================================

st.header("2. Informations sur l'API et le modèle")

try:
    api_info = api_get("/")

    st.success("Configuration du modèle")

    col1, col2, col3 = st.columns(3)

    col1.metric("Modèle", api_info["model"])
    col1.metric("Nombre de variables", api_info["n_features"])

    col2.metric(
        "Variables obligatoires",
        api_info["n_required_features"]
    )
    col2.metric(
        "Variables recommandées",
        api_info["n_recommended_features"]
    )

    col3.metric(
        "Seuil métier",
        api_info["business_threshold"]
    )

    with st.expander("Réponse complète de l'API"):
        st.json(api_info)

except requests.exceptions.Timeout:
    st.warning(
        "L'API met trop de temps à répondre. "
        "Le service Render est peut-être en veille."
    )

except requests.exceptions.RequestException as error:
    st.error(f"Impossible de récupérer les informations : {error}")


# ==================================================
# 3. TEST DE PREDICTION
# ==================================================

st.header("3. Test de prédiction")

# Les scénarios permettent de reproduire depuis Streamlit
# les principaux tests déjà réalisés dans Swagger.

test_scenario = st.selectbox(
    "Choisissez un scénario de test",
    [
        "Prédiction nominale",
        "Variable obligatoire absente",
        "Type invalide",
        "Valeur booléenne",
        "Variable inconnue",
        "Variables recommandées",
        "Variable optionnelle",
        "Multi-clients"
    ]
)


# ==================================================
# DONNEES DE BASE
# ==================================================

base_client = {
    "PAYMENT_RATE": 0.05,
    "EXT_SOURCE_MEAN": 0.60,
    "DAYS_BIRTH": -15000,
    "DAYS_EMPLOYED": -2000,
    "AMT_ANNUITY": 15000
}


# ==================================================
# CONSTRUCTION DU SCENARIO
# ==================================================

if test_scenario == "Prédiction nominale":

    clients = [base_client]

elif test_scenario == "Variable obligatoire absente":

    # DAYS_BIRTH est supprimée pour vérifier la validation Pydantic.
    client = base_client.copy()
    del client["DAYS_BIRTH"]
    clients = [client]

elif test_scenario == "Type invalide":

    # Une chaîne remplace une valeur numérique.
    client = base_client.copy()
    client["PAYMENT_RATE"] = "bonjour"
    clients = [client]

elif test_scenario == "Valeur booléenne":

    # Un booléen est volontairement transmis à l'API.
    client = base_client.copy()
    client["PAYMENT_RATE"] = True
    clients = [client]

elif test_scenario == "Variable inconnue":

    # Cette variable n'existe pas dans feature_names du modèle.
    client = base_client.copy()
    client["PAYMENT_RAT"] = 0.05
    clients = [client]

elif test_scenario == "Variables recommandées":

    client = base_client.copy()

    client.update({
        "EXT_SOURCE_1": 0.50,
        "EXT_SOURCE_2": 0.60,
        "EXT_SOURCE_3": 0.70,
        "DAYS_ID_PUBLISH": -3000,
        "DAYS_REGISTRATION": -4000,
        "DAYS_LAST_PHONE_CHANGE": -500
    })

    clients = [client]

elif test_scenario == "Variable optionnelle":

    client = base_client.copy()
    client["BURO_DAYS_CREDIT_MEAN"] = -1200
    clients = [client]

else:

    # Ce scénario vérifie le traitement de plusieurs clients
    # dans une seule requête POST /predict.
    clients = [
        base_client,
        {
            "PAYMENT_RATE": 0.12,
            "EXT_SOURCE_MEAN": 0.30,
            "DAYS_BIRTH": -10000,
            "DAYS_EMPLOYED": -500,
            "AMT_ANNUITY": 25000
        }
    ]


payload = {
    "requested_by": f"test_streamlit_{test_scenario}",
    "clients": clients
}


# ==================================================
# AFFICHAGE DES DONNEES
# ==================================================

st.subheader("Données envoyées à l'API")

with st.expander("Afficher le JSON envoyé"):
    st.json(payload)


# ==================================================
# LANCEMENT DU TEST
# ==================================================

if st.button("Lancer le test"):

    try:

        response = api_predict(payload)

        # On affiche toujours le code HTTP.
        # Cela permet de distinguer les tests réussis (200)
        # des tests de validation rejetés par l'API (422).
        st.subheader("Résultat du test")

        st.write(
            f"Code HTTP : **{response.status_code}**"
        )

        result = response.json()

        # ==================================================
        # TESTS DE PREDICTION REUSSIS
        # ==================================================

        if response.status_code == 200:

            st.success(
                "Prédiction réalisée avec succès"
            )

            predictions = result["predictions"]

            # Un résultat est affiché pour chaque client.
            for prediction in predictions:

                st.divider()

                st.subheader(
                    f"Client {prediction['client_index'] + 1}"
                )

                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "Probabilité de défaut",
                    prediction["default_probability"]
                )

                col2.metric(
                    "Seuil métier",
                    prediction["business_threshold"]
                )

                if prediction["decision"] == "ACCEPTED":
                    col3.success(
                        f"Décision : {prediction['decision']}"
                    )
                else:
                    col3.error(
                        f"Décision : {prediction['decision']}"
                    )

                # La couverture mesure la proportion pondérée
                # des variables importantes effectivement fournies.
                col1.metric(
                    "Couverture des variables",
                    f"{prediction['feature_coverage_rate']} %"
                )

                col2.metric(
                    "Complétude des données",
                    prediction["data_completeness_level"]
                )

                col3.metric(
                    "Variables optionnelles absentes",
                    prediction["n_missing_optional_features"]
                )

                if prediction["missing_recommended_features"]:
                    st.warning(
                        "Variables recommandées absentes : "
                        f"{prediction['missing_recommended_features']}"
                    )
                else:
                    st.success(
                        "Toutes les variables recommandées sont présentes."
                    )

                st.subheader("Warning")
                st.warning(prediction["warning"])

        # ==================================================
        # TESTS DE VALIDATION REJETES
        # ==================================================

        elif response.status_code == 422:

            st.warning(
                "La requête a été correctement rejetée par l'API."
            )

            # La réponse 422 permet de vérifier que FastAPI/Pydantic
            # détecte correctement les données invalides.
            st.json(result)

        # ==================================================
        # AUTRES ERREURS HTTP
        # ==================================================

        else:

            st.error(
                f"L'API a retourné une erreur HTTP "
                f"{response.status_code}."
            )

            st.json(result)

        # ==================================================
        # REPONSE COMPLETE
        # ==================================================

        with st.expander("Réponse complète de l'API"):
            st.json(result)

    except requests.exceptions.Timeout:

        st.error(
            "L'API met trop de temps à répondre. "
            "Le service Render est peut-être en veille. "
            "Attendez quelques secondes puis relancez le test."
        )

    except requests.exceptions.RequestException as error:

        st.error(
            f"Erreur lors de la communication avec l'API : {error}"
        )

    except ValueError:

        st.error(
            "La réponse reçue par Streamlit n'est pas un JSON valide."
        )

    except KeyError as error:

        st.error(
            f"La réponse de l'API ne contient pas la clé attendue : {error}"
        )

        st.json(result)
