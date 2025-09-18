from event_generator import generate_activity_payloads
import streamlit as st
import pandas as pd
from faker import Faker
import random
import requests

fake = Faker()

st.set_page_config(page_title="Netcore Dummy Data Generator", layout="wide")
st.title("📧 Netcore Dummy Contact & Event Generator")

# Step 1: User Inputs
num_users = st.number_input("How many users to generate?", min_value=100, max_value=30000, step=1000, value=1000)

custom_attr_1 = st.text_input("Custom Attribute 1 Name (e.g., SEGMENT)")
custom_values_1 = st.text_input("Possible values for Attribute 1 (comma separated)")

custom_attr_2 = st.text_input("Custom Attribute 2 Name (e.g., TIER)")
custom_values_2 = st.text_input("Possible values for Attribute 2 (comma separated)")

website = st.text_input("Enter website/brand (e.g., shop.example.com)")
asset_id = st.text_input("Enter Netcore Asset ID")
api_key = st.text_input("Enter Netcore API Key")

# Generate Dummy Users
generate = st.button("🚀 Generate Dummy Users")

if generate:
    emails = [f"user{i}@example.com" for i in range(1, num_users + 1)]
    st.session_state["dummy_users"] = emails  # Save in session
    phones = [fake.msisdn()[0:10] for _ in range(num_users)]
    languages = random.choices(['ENGLISH', 'SPANISH', 'GERMAN', 'FRENCH'], k=num_users)

    attr1_vals = [val.strip().upper() for val in custom_values_1.split(",") if val.strip()]
    attr2_vals = [val.strip().upper() for val in custom_values_2.split(",") if val.strip()]

    attr1_list = random.choices(attr1_vals, k=num_users)
    attr2_list = random.choices(attr2_vals, k=num_users)

    df = pd.DataFrame({
        "EMAIL": emails,
        "PHONE": phones,
        "LANGUAGE": languages,
        custom_attr_1.upper(): attr1_list,
        custom_attr_2.upper(): attr2_list
    })

    st.success("✅ Dummy users generated")
    st.write(df.head(10))

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name='dummy_contact_list.csv',
        mime='text/csv'
    )

# Generate Sample Events
st.header("🧪 Generate Sample Product Purchase Events")

img1 = st.text_input("Product 1 Image URL")
url1 = st.text_input("Product 1 Product URL")
name1 = st.text_input("Product 1 Name")
price1 = st.number_input("Product 1 Price", min_value=1, max_value=1000, value=79)

img2 = st.text_input("Product 2 Image URL")
url2 = st.text_input("Product 2 Product URL")
name2 = st.text_input("Product 2 Name")
price2 = st.number_input("Product 2 Price", min_value=1, max_value=1000, value=115)

num_activity_users = st.number_input("How many users to generate activity for?", min_value=1, max_value=1000, step=50, value=50)

if st.button("📦 Generate Event JSON"):
    if not (asset_id and api_key):
        st.error("❗ Please enter Asset ID and API Key first.")
        st.stop()

    if "dummy_users" not in st.session_state:
        st.error("❗ Please generate dummy users first.")
        st.stop()

    products = [
        {"ImageURL": img1, "productURL": url1, "productName": name1, "price": price1},
        {"ImageURL": img2, "productURL": url2, "productName": name2, "price": price2}
    ]

    users = random.sample(st.session_state["dummy_users"], k=min(num_activity_users, len(st.session_state["dummy_users"])))
    event_json = generate_activity_payloads(asset_id, users, products)

    st.success("✅ Sample Event JSON Generated")
    st.json(event_json[:3])  # Show top 3 for preview

    json_str = str(event_json).replace("'", '"')

    st.download_button(
        label="📥 Download JSON",
        data=json_str,
        file_name="sample_event_payloads.json",
        mime="application/json"
    )

    if st.button("🚀 Push to Netcore"):
        headers = {
            "Content-Type": "application/json",
            "Authorization": api_key,
            "X-Netcore-Asset-Id": asset_id
        }

        response = requests.post(
            url="https://api2.netcoresmartech.com/v1/activity/upload",
            headers=headers,
            json=event_json
        )

        if response.status_code == 200:
            st.success("🎉 Data pushed to Netcore successfully!")
        else:
            st.error(f"❌ Failed. Status Code: {response.status_code}")
            try:
                st.json(response.json())
            except Exception as e:
                st.error(f"⚠️ Could not parse error response: {e}")
