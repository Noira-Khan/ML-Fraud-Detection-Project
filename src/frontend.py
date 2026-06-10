import streamlit as st
import requests
import pandas as pd

# --- Page Configuration ---
st.set_page_config(page_title="Fraud Detective Portal", page_icon="🛡️", layout="wide")

st.title("🛡️ Real-Time Fraud Detection Portal")
st.markdown("Upload a transaction file or enter features manually to detect anomalies.")

# The URL of your running FastAPI server
API_URL = "http://localhost:8000/predict"

# --- Create Tabs for the UI ---
tab1, tab2 = st.tabs(["📁 Batch Processing (CSV/Excel)", "✍️ Manual Entry"])

# ==========================================
# TAB 1: CSV / EXCEL UPLOAD
# ==========================================
with tab1:
    st.header("Upload Transaction Data")
    st.info("Upload a CSV file containing 30 feature columns (V1-V28, Amount, Time).")
    
    uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx"])
    
    if uploaded_file is not None:
        # Read the file
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
            
        st.write("### Data Preview")
        st.dataframe(df.head())
        
        if st.button("Scan First Row for Fraud"):
            # Extract the first row as a list of floats
            features = df.iloc[0].tolist()
            
            if len(features) != 30:
                st.error(f"Data Error: Expected 30 columns, but found {len(features)}. Please check your dataset.")
            else:
                payload = {"features": features}
                with st.spinner('Analyzing transaction...'):
                    try:
                        response = requests.post(API_URL, json=payload)
                        result = response.json()
                        
                        # Display the results beautifully
                        st.divider()
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric(label="Fraud Probability", value=f"{result['fraud_probability'] * 100:.2f}%")
                        
                        with col2:
                            if result['is_fraud']:
                                st.error("🚨 HIGH RISK: Fraudulent Transaction Detected!")
                            else:
                                st.success("✅ LOW RISK: Transaction Appears Legitimate.")
                        
                        # --- Display the SHAP Explanations ---
                        st.write("### Key Factors Driving This Prediction:")
                        for reason in result.get('top_drivers', []):
                            st.write(f"- **{reason['impact']}** (Driven by Feature: `{reason['feature']}`)")
                                
                    except requests.exceptions.ConnectionError:
                        st.error("Failed to connect to API. Is your FastAPI server running in another terminal?")
                    except Exception as e:
                        st.error(f"An error occurred: {e}")

# ==========================================
# TAB 2: MANUAL ENTRY
# ==========================================
with tab2:
    st.header("Manual Feature Input")
    st.write("For testing purposes, paste a comma-separated list of 30 features below.")
    
    # Default dummy payload (Legitimate Transaction Profile)
    default_input = "0.0, -1.2, 0.5, 2.1, -0.8, 1.1, 0.0, -0.3, 0.9, -1.0, 0.2, 0.0, 0.5, -0.4, 1.2, 0.0, -0.5, 0.8, 0.1, -0.2, 0.3, 0.0, -0.1, 0.4, 0.0, 0.0, -0.2, 0.1, 150.00, 0.0"
    
    user_input = st.text_area("Enter 30 features (comma separated):", value=default_input)
    
    if st.button("Run Manual Prediction"):
        try:
            # Convert the string input into a list of floats
            features_list = [float(x.strip()) for x in user_input.split(',')]
            
            if len(features_list) != 30:
                st.warning(f"Expected 30 features, but got {len(features_list)}.")
            else:
                payload = {"features": features_list}
                with st.spinner('Calculating Probability and Explanations...'):
                    response = requests.post(API_URL, json=payload)
                    result = response.json()
                    
                    st.divider()
                    if result.get('is_fraud'):
                        st.error(f"🚨 FRAUD DETECTED (Probability: {result['fraud_probability'] * 100:.2f}%)")
                    else:
                        st.success(f"✅ SAFE (Probability: {result['fraud_probability'] * 100:.2f}%)")
                    
                    # --- Display the SHAP Explanations ---
                    st.write("### Key Factors Driving This Prediction:")
                    for reason in result.get('top_drivers', []):
                        st.write(f"- **{reason['impact']}** (Driven by Feature: `{reason['feature']}`)")
                        
        except ValueError:
            st.error("Invalid input. Please ensure only numbers and commas are used.")
        except requests.exceptions.ConnectionError:
            st.error("Failed to connect to API. Is your FastAPI server running in another terminal?")
        except Exception as e:
            st.error(f"An error occurred: {e}")     
            