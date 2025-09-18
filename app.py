from event_generator import generate_activity_payloads
import streamlit as st
import pandas as pd
from faker import Faker
import random
import requests

fake = Faker()
st.set_page_config(page_title="Netcore Dummy Data Generator", layout="wide")
st.title("📧 Netcore Dummy Contact Generator")

# User input for contact generation
num_users = st.number_input("How many users to generate?", min_value=100, max_value=30000, step=1000, value=1000)

custom_attr_1 = st.text_input("Custom Attribute 1 Name (e.g., SEGMENT)")
custom_values_1 = st.text_input("Possible values for Attribute 1 (comma separated)")

custom_attr_2 = st.text_input("Custom Attribute 2 Name (e.g., TIER)")
custom_values_2 = st.text_input("Possible values for Attribute 2 (comma separated)")

website = st.text_input("Enter website/brand (e.g., shop.example.com)")
asset_id = st.text_input("Enter Netcore Asset ID")
api_key = st.text_input("Enter Netcore API Key")

if st.button("🚀 Generate Dummy Users"):
    emails = [f"user{i}@example.com" for i in range(1, num_users + 1)]
    st.session_state["dummy_users"] = emails
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

    st.session_state["dummy_df"] = df
    st.success("Dummy contact list generated ✅")
    st.write(df.head(10))

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download CSV", data=csv, file_name='dummy_contact_list.csv', mime='text/csv')

# Product Inputs
st.header("📦 Enter Product Details (at least 1)")

products = []
for i in range(2):
    with st.expander(f"Product {i+1}"):
        name = st.text_input(f"Product {i+1} Name", key=f"name_{i}")
        url = st.text_input(f"Product {i+1} URL", key=f"url_{i}")
        img = st.text_input(f"Product {i+1} Image URL", key=f"img_{i}")
        price = st.number_input(f"Product {i+1} Price", min_value=1, max_value=1000, value=99, key=f"price_{i}")
        if name and url and img:
            products.append({"productName": name, "productURL": url, "ImageURL": img, "price": price})

if len(products) == 0:
    st.warning("Please add at least one product.")
else:
    st.success(f"{len(products)} product(s) saved.")

# Event Payload Generator
st.header("🧪 Generate Sample Product Purchase Event JSON")
num_activity_users = st.number_input("Number of users for activity JSON", min_value=1, max_value=1000, value=50)

if st.button("📦 Generate Event JSON"):
    if not asset_id or not api_key:
        st.error("⚠️ Please enter both Asset ID and API Key first.")
    elif "dummy_users" not in st.session_state:
        st.error("⚠️ Please generate dummy users first.")
    elif not products:
        st.error("⚠️ Please enter at least one product.")
    else:
        users = random.sample(st.session_state["dummy_users"], k=min(num_activity_users, len(st.session_state["dummy_users"])))
        event_json = generate_activity_payloads(asset_id, users, products)

        st.session_state["event_json"] = event_json

        st.success("Sample Event JSON Generated")
        st.json(event_json[:3])

        json_str = str(event_json).replace("'", '"')
        st.download_button("📥 Download JSON", data=json_str, file_name="event_payload.json", mime="application/json")

# Push to Netcore
if st.button("🚀 Push to Netcore"):
    if not asset_id or not api_key:
        st.error("⚠️ Please enter both Asset ID and API Key.")
    elif "event_json" not in st.session_state:
        st.error("⚠️ Please generate event data first.")
    else:
        headers = {
            "Content-Type": "application/json",
            "Authorization": api_key,
            "X-Netcore-Asset-Id": asset_id
        }
        try:
            response = requests.post(
                url="https://api2.netcoresmartech.com/v1/activity/upload",
                headers=headers,
                json=st.session_state["event_json"]
            )

            if response.status_code == 200:
                st.success("✅ Data pushed to Netcore successfully!")
            else:
                st.error(f"❌ Failed with status code: {response.status_code}")
                st.write(response.text)
        except Exception as e:
            st.error(f"❌ Exception occurred: {e}")
