"""
Streamlit frontend for the SuperKart Product-Store Sales Forecast model.
Talks to the Flask backend's /predict (single) and /predict_batch (batch) endpoints.
"""

import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="SuperKart Sales Forecast", layout="centered")
st.title(":shopping_trolley: SuperKart - Product-Store Sales Forecast")
st.write(
    "Predict `Product_Store_Sales_Total` for a single product-store combination, "
    "or upload a CSV for batch predictions."
)

backend_url = st.text_input(
    "Backend API URL", value="http://localhost:5000", help="URL where the Flask backend is running."
).rstrip("/")

tab_single, tab_batch = st.tabs(["Single Prediction", "Batch Prediction"])

# ------------------------------------------------------------------ Single prediction --
with tab_single:
    st.subheader("Enter product & store details")

    col1, col2 = st.columns(2)
    with col1:
        product_weight = st.number_input("Product Weight", min_value=0.0, value=12.5)
        product_sugar_content = st.selectbox(
            "Product Sugar Content", ["Low Sugar", "Regular", "No Sugar"]
        )
        product_allocated_area = st.number_input(
            "Product Allocated Area", min_value=0.0, max_value=1.0, value=0.05, format="%.3f"
        )
        product_mrp = st.number_input("Product MRP", min_value=0.0, value=150.0)
        store_size = st.selectbox("Store Size", ["Small", "Medium", "High"])
    with col2:
        store_location_city_type = st.selectbox(
            "Store Location City Type", ["Tier 1", "Tier 2", "Tier 3"]
        )
        store_type = st.selectbox(
            "Store Type",
            ["Food Mart", "Supermarket Type1", "Supermarket Type2", "Departmental Store"],
        )
        product_id_char = st.selectbox("Product Id Prefix", ["FD", "DR", "NC"])
        store_age_years = st.number_input("Store Age (Years)", min_value=0, value=15)
        product_type_category = st.selectbox(
            "Product Type Category", ["Perishables", "Non Perishables"]
        )

    if st.button("Predict Sales", type="primary"):
        payload = {
            "Product_Weight": product_weight,
            "Product_Sugar_Content": product_sugar_content,
            "Product_Allocated_Area": product_allocated_area,
            "Product_MRP": product_mrp,
            "Store_Size": store_size,
            "Store_Location_City_Type": store_location_city_type,
            "Store_Type": store_type,
            "Product_Id_char": product_id_char,
            "Store_Age_Years": store_age_years,
            "Product_Type_Category": product_type_category,
        }
        try:
            response = requests.post(f"{backend_url}/predict", json=payload, timeout=30)
            if response.status_code == 200:
                prediction = response.json()["Product_Store_Sales_Total_Prediction"]
                st.success(f"Predicted Product_Store_Sales_Total: **{prediction:,.2f}**")
            else:
                st.error(f"Backend returned an error: {response.json()}")
        except Exception as exc:  # noqa: BLE001
            st.error(f"Could not reach the backend API at {backend_url}: {exc}")

# ------------------------------------------------------------------- Batch prediction --
with tab_batch:
    st.subheader("Upload a CSV for batch predictions")
    st.caption(
        "The CSV must contain the columns: Product_Weight, Product_Sugar_Content, "
        "Product_Allocated_Area, Product_MRP, Store_Size, Store_Location_City_Type, "
        "Store_Type, Product_Id_char, Store_Age_Years, Product_Type_Category."
    )

    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
    if uploaded_file is not None:
        preview_df = pd.read_csv(uploaded_file)
        st.write("Preview of uploaded data:")
        st.dataframe(preview_df.head())

        if st.button("Run Batch Prediction", type="primary"):
            uploaded_file.seek(0)
            files = {"file": (uploaded_file.name, uploaded_file, "text/csv")}
            try:
                response = requests.post(f"{backend_url}/predict_batch", files=files, timeout=60)
                if response.status_code == 200:
                    st.success("Batch predictions ready.")
                    st.download_button(
                        label="Download predictions CSV",
                        data=response.content,
                        file_name="superkart_batch_predictions.csv",
                        mime="text/csv",
                    )
                else:
                    st.error(f"Backend returned an error: {response.json()}")
            except Exception as exc:  # noqa: BLE001
                st.error(f"Could not reach the backend API at {backend_url}: {exc}")
