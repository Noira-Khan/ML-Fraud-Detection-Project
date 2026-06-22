import pandas as pd
import requests
import streamlit as st


API_URL = "http://localhost:8000/predict"
EXPECTED_FEATURES = 30

st.set_page_config(
    page_title="Fraud Detective Portal",
    page_icon="🛡️",
    layout="wide",
)

st.title("🛡️ Real-Time Fraud Detection Portal")
st.markdown(
    "Upload a transaction file or enter features manually to detect anomalies."
)

with st.sidebar:
    st.title("Navigation")
    page = st.radio(
        "Select Section",
        [
            "Overview",
            "Fraud Detection",
            "Model Metrics",
            "Architecture",
            "Future Roadmap",
        ],
    )

if page == "Architecture":
    st.header("Solution Architecture")
    st.image("assets/architecture.png")

elif page == "Model Metrics":
    st.header("Model Metrics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Accuracy", "99.2%")
    col2.metric("Precision", "95%")
    col3.metric("Recall", "92%")
    col4.metric("ROC-AUC", "98%")

elif page == "Future Roadmap":
    st.markdown(
        """
        ## Product Roadmap

        **Phase 1**
        - Fraud prediction

        **Phase 2**
        - Analyst dashboard

        **Phase 3**
        - Real-time streaming

        **Phase 4**
        - LLM-powered fraud explanations

        **Phase 5**
        - AI Fraud Copilot
        """
    )

else:
    tab1, tab2 = st.tabs(
        ["📁 Batch Processing (CSV/Excel)", "✍️ Manual Entry"]
    )

    with tab1:
        st.header("Upload Transaction Data")
        st.info(
            "Upload a file containing 30 feature columns "
            "(Time, V1-V28, and Amount)."
        )

        uploaded_file = st.file_uploader(
            "Choose a file", type=["csv", "xlsx"]
        )

        if uploaded_file is not None:
            try:
                if uploaded_file.name.lower().endswith(".csv"):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)

                st.write("### Data Preview")
                st.dataframe(df.head())

                if st.button("Scan First Row for Fraud"):
                    features = df.iloc[0].astype(float).tolist()

                    if len(features) != EXPECTED_FEATURES:
                        st.error(
                            f"Expected {EXPECTED_FEATURES} columns, but found "
                            f"{len(features)}. Remove non-feature columns such as "
                            "'Class' before uploading."
                        )
                    else:
                        with st.spinner("Analyzing transaction..."):
                            response = requests.post(
                                API_URL,
                                json={"features": features},
                                timeout=30,
                            )
                            response.raise_for_status()
                            result = response.json()

                        st.divider()
                        result_col1, result_col2 = st.columns(2)
                        probability = float(result.get("fraud_probability", 0))

                        with result_col1:
                            st.metric(
                                "Fraud Probability",
                                f"{probability * 100:.2f}%",
                            )

                        with result_col2:
                            if result.get("is_fraud", False):
                                st.error(
                                    "🚨 HIGH RISK: Fraudulent transaction detected!"
                                )
                            else:
                                st.success(
                                    "✅ LOW RISK: Transaction appears legitimate."
                                )

                        st.write("### Key Factors Driving This Prediction")
                        for reason in result.get("top_drivers", []):
                            st.write(
                                f"- **{reason.get('impact', 'Unknown')}** "
                                f"(Feature: `{reason.get('feature', 'Unknown')}`)"
                            )

            except (ValueError, TypeError):
                st.error("The uploaded feature values must all be numeric.")
            except requests.exceptions.ConnectionError:
                st.error(
                    "Could not connect to the API. Make sure FastAPI is running "
                    "at http://localhost:8000."
                )
            except requests.exceptions.RequestException as error:
                st.error(f"The prediction request failed: {error}")
            except Exception as error:
                st.error(f"Could not process the uploaded file: {error}")

    with tab2:
        st.header("Manual Feature Input")
        st.write("Paste a comma-separated list of 30 features below.")

        default_input = (
            "0.0, -1.2, 0.5, 2.1, -0.8, 1.1, 0.0, -0.3, 0.9, -1.0, "
            "0.2, 0.0, 0.5, -0.4, 1.2, 0.0, -0.5, 0.8, 0.1, -0.2, "
            "0.3, 0.0, -0.1, 0.4, 0.0, 0.0, -0.2, 0.1, 150.00, 0.0"
        )
        user_input = st.text_area(
            "Enter 30 features (comma separated):", value=default_input
        )

        if st.button("Run Manual Prediction"):
            try:
                features = [float(value.strip()) for value in user_input.split(",")]

                if len(features) != EXPECTED_FEATURES:
                    st.warning(
                        f"Expected {EXPECTED_FEATURES} features, but got "
                        f"{len(features)}."
                    )
                else:
                    with st.spinner("Calculating probability and explanations..."):
                        response = requests.post(
                            API_URL,
                            json={"features": features},
                            timeout=30,
                        )
                        response.raise_for_status()
                        result = response.json()

                    probability = float(result.get("fraud_probability", 0))
                    st.divider()
                    if result.get("is_fraud", False):
                        st.error(
                            f"🚨 FRAUD DETECTED "
                            f"(Probability: {probability * 100:.2f}%)"
                        )
                    else:
                        st.success(
                            f"✅ SAFE (Probability: {probability * 100:.2f}%)"
                        )

                    st.write("### Key Factors Driving This Prediction")
                    for reason in result.get("top_drivers", []):
                        st.write(
                            f"- **{reason.get('impact', 'Unknown')}** "
                            f"(Feature: `{reason.get('feature', 'Unknown')}`)"
                        )

            except ValueError:
                st.error("Invalid input. Use only numbers separated by commas.")
            except requests.exceptions.ConnectionError:
                st.error(
                    "Could not connect to the API. Make sure FastAPI is running "
                    "at http://localhost:8000."
                )
            except requests.exceptions.RequestException as error:
                st.error(f"The prediction request failed: {error}")
            except Exception as error:
                st.error(f"An unexpected error occurred: {error}")
