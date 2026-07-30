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

# Style CSS léger pour améliorer la lisibilité.
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    .main-title {
        font-size: 2.4rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        color: #6b7280;
        font-size: 1.05rem;
        margin-bottom: 2rem;
    }

    .section-title {
        margin-top: 2rem;
        margin-bottom: 1rem;
    }

    .status-card {
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #d1d5db;
        background-color: #f9fafb;
    }

    .decision-accepted {
        color: #15803d;
        font-size: 1.3rem;
        font-weight: 700;
    }

    .decision-refused {
        color: #b91c1c;
        font-size: 1.3rem;
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True
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
    return requests.post(
        f"{API_URL}/predict",
        json=payload,
        timeout=60
    )


# ==================================================
# EN-TETE
# ==================================================

st.markdown(
    '<div class="main-title">💳 Home Credit Scoring</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    "Interface de test de l'API FastAPI de scoring crédit"
    "</div>",
    unsafe_allow_html=True
)


# ==================================================
# 1. SANTE DE L'API
# ==================================================

st.markdown(
    '<h2 class="section-title">1. Santé de l\'API</h2>',
    unsafe_allow_html=True
)

try:
    health = api_get("/health")

    if health.get("status") == "healthy":
        st.success("🟢 API opérationnelle et accessible")
    else:
        st.warning(f"🟠 Statut API inattendu : {health}")

except requests.exceptions.Timeout:
    st.warning(
        "🟠 L'API met du temps à répondre. "
        "Le service Render est peut-être en sortie de veille."
    )

except requests.exceptions.RequestException as error:
    st.error(f"🔴 Impossible de contacter l'API : {error}")


# ==================================================
# 2. INFORMATIONS API ET MODELE
# ==================================================

st.markdown(
    '<h2 class="section-title">2. Informations sur l\'API et le modèle</h2>',
    unsafe_allow_html=True
)

try:
    api_info = api_get("/")

    st.success("🟢 Configuration du modèle récupérée")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Modèle",
        api_info["model"]
    )

    col2.metric(
        "Variables",
        api_info["n_features"]
    )

    col3.metric(
        "Variables obligatoires",
        api_info["n_required_features"]
    )

    col4.metric(
        "Seuil métier",
        api_info["business_threshold"]
    )

    st.caption(
        f"{api_info['n_recommended_features']} variables recommandées "
        "pour améliorer la couverture des données."
    )

    with st.expander("🔎 Voir la réponse complète de l'API"):
        st.json(api_info)

except requests.exceptions.Timeout:
    st.warning(
        "🟠 L'API met trop de temps à répondre. "
        "Le service Render est peut-être en veille."
    )

except requests.exceptions.RequestException as error:
    st.error(
        f"🔴 Impossible de récupérer les informations : {error}"
    )


# ==================================================
# 3. TEST DE PREDICTION
# ==================================================

st.markdown(
    '<h2 class="section-title">3. Test de prédiction</h2>',
    unsafe_allow_html=True
)

st.info(
    "Sélectionnez un scénario pour tester différents comportements "
    "de validation et de prédiction de l'API."
)

test_scenario = st.selectbox(
    "Scénario de test",
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

    client = base_client.copy()
    del client["DAYS_BIRTH"]
    clients = [client]

elif test_scenario == "Type invalide":

    client = base_client.copy()
    client["PAYMENT_RATE"] = "bonjour"
    clients = [client]

elif test_scenario == "Valeur booléenne":

    client = base_client.copy()
    client["PAYMENT_RATE"] = True
    clients = [client]

elif test_scenario == "Variable inconnue":

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
# APERCU DU TEST
# ==================================================

st.subheader(f"🧪 Scénario : {test_scenario}")

with st.expander("📤 Voir le JSON envoyé à l'API"):
    st.json(payload)


# ==================================================
# LANCEMENT DU TEST
# ==================================================

if st.button(
    "🚀 Lancer le test",
    type="primary",
    use_container_width=True
):

    try:

        response = api_predict(payload)

        st.divider()

        # ==================================================
        # STATUT HTTP
        # ==================================================

        if response.status_code == 200:
            st.success(
                f"🟢 Test réussi — HTTP {response.status_code}"
            )

        elif response.status_code == 422:
            st.warning(
                f"🟠 Requête correctement rejetée — HTTP {response.status_code}"
            )

        else:
            st.error(
                f"🔴 Erreur API — HTTP {response.status_code}"
            )

        result = response.json()


        # ==================================================
        # RESULTATS DE PREDICTION
        # ==================================================

        if response.status_code == 200:

            predictions = result["predictions"]

            st.subheader("📊 Résultat du scoring")

            for prediction in predictions:

                st.divider()

                st.markdown(
                    f"### Client {prediction['client_index'] + 1}"
                )

                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "Probabilité de défaut",
                    f"{prediction['default_probability']:.6f}"
                )

                col2.metric(
                    "Seuil métier",
                    f"{prediction['business_threshold']:.6f}"
                )

                if prediction["decision"] == "ACCEPTED":

                    col3.markdown(
                        '<div class="decision-accepted">'
                        "🟢 ACCEPTED"
                        "</div>",
                        unsafe_allow_html=True
                    )

                else:

                    col3.markdown(
                        '<div class="decision-refused">'
                        "🔴 REFUSED"
                        "</div>",
                        unsafe_allow_html=True
                    )

                col1, col2, col3 = st.columns(3)

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
                        "⚠️ Variables recommandées absentes : "
                        f"{', '.join(prediction['missing_recommended_features'])}"
                    )

                else:

                    st.success(
                        "✅ Toutes les variables recommandées sont présentes."
                    )

                with st.expander("⚠️ Voir le warning métier"):
                    st.warning(prediction["warning"])


        # ==================================================
        # ERREURS DE VALIDATION
        # ==================================================

        elif response.status_code == 422:

            st.subheader("🔎 Détail de la validation")

            st.info(
                "L'API a correctement détecté une donnée invalide "
                "et a rejeté la requête."
            )

            st.json(result)


        # ==================================================
        # AUTRES ERREURS HTTP
        # ==================================================

        else:

            st.subheader("❌ Détail de l'erreur")

            st.json(result)


        # ==================================================
        # REPONSE COMPLETE
        # ==================================================

        with st.expander("📥 Voir la réponse complète de l'API"):

            st.json(result)

    except requests.exceptions.Timeout:

        st.error(
            "⏱️ L'API met trop de temps à répondre. "
            "Le service Render est peut-être en veille. "
            "Attendez quelques secondes puis relancez le test."
        )

    except requests.exceptions.RequestException as error:

        st.error(
            f"🔴 Erreur lors de la communication avec l'API : {error}"
        )

    except ValueError:

        st.error(
            "🔴 La réponse reçue par Streamlit n'est pas un JSON valide."
        )

    except KeyError as error:

        st.error(
            f"🔴 La réponse de l'API ne contient pas la clé attendue : {error}"
        )