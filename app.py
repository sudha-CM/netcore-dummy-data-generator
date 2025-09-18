from event_generator import generate_activity_payloads
import streamlit as st
import pandas as pd
from faker import Faker
import random
import requests

fake = Faker()

st.set_page_config(page_title="Netcore Dummy Data Generator", layout="wide")
st.title("📧 Netcore Dummy Contact Generator")

# Step 1: Get user inputs
num_users = st.number_input("How many users to generate?", min_value=100, max_value=30000, step=1000, value=1000)

custom_attr_1 = st.text_input("Custom Attribute 1 Name (e.g., SEGMENT)")
custom_values_1 = st.text_input("Possible values for Attribute 1 (comma separated)")

custom_attr_2 = st.text_input("Custom Attribute 2 Name (e.g., TIER)")
custom_values_2 = st.text_input("Possible values for Attribute 2 (comma separated)")

website = st.text_input("Enter website/brand (e.g., shop.example.com)")
asset_id = st.text_input("Enter Netcore Asset ID")
api_key = st.text_input("Enter Netcore API Key")

generate = st.button("🚀 Generate Dummy Users")

if generate:
    emails = [f"user{i}@example.com" for i in range(1, num_users + 1)]
    st.session_state["dummy_users"] = emails # ✅ Save to session state
    phones = [fake.msisdn()[0:10] for _ in range(num_users)]
    languages = random.choices(['ENGLISH', 'SPANISH', 'GERMAN', 'FRENCH'], k=num_users)

    attr1_vals = [val.strip().upper() for val in custom_values_1.split(",") if val.strip()]
    attr2_vals = [val.strip().upper() for val in custom_values_2.split(",") if val.strip()]

    attr1_list = random.choices(attr1_vals, k=num_users)
    attr2_list = random.choices(attr2_vals, k=num_users)

    # Create DataFrame
    df = pd.DataFrame({
        "EMAIL": emails,
        "PHONE": phones,
        "LANGUAGE": languages,
        custom_attr_1.upper(): attr1_list,
        custom_attr_2.upper(): attr2_list
    })

    st.success("Dummy contact list generated ✅")
    st.write(df.head(10))

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name='dummy_contact_list.csv',
        mime='text/csv'
    )
st.header("📦 Add Up to 2 Product Details")

product_inputs = []

for i in range(2):
    st.subheader(f"Product {i+1}")
    title = st.text_input(f"Title {i+1}", key=f"title_{i}")
    price = st.text_input(f"Price {i+1}", key=f"price_{i}")
    category = st.text_input(f"Category {i+1}", key=f"category_{i}")
    imageUrl = st.text_input(f"Image URL {i+1}", key=f"image_url_{i}")

    product_inputs.append({
        "title": title,
        "price": price,
        "category": category,
        "imageUrl": imageUrl
    })

if st.button("Submit Product Details"):
    valid_products = [p for p in product_inputs if p["title"] and p["price"] and p["category"]]
    
    if valid_products:
        st.success(f"{len(valid_products)} Product(s) Submitted ✅")
        for idx, prod in enumerate(valid_products, 1):
            st.markdown(f"**Product {idx}:**")
            st.json(prod)
    else:
        st.warning("Please enter title, price, and category for at least one product.")

st.header("🧪 Generate Sample Product Purchase Activity JSON")

# Add UI to capture product info
products = []

col1, col2 = st.columns(2)
with col1:
    img1 = st.text_input("Product 1 Image URL")
    url1 = st.text_input("Product 1 Product URL")
    name1 = st.text_input("Product 1 Name")
    price1 = st.number_input("Product 1 Price", min_value=1, max_value=1000, value=79)

with col2:
    img2 = st.text_input("Product 2 Image URL")
    url2 = st.text_input("Product 2 Product URL")
    name2 = st.text_input("Product 2 Name")
    price2 = st.number_input("Product 2 Price", min_value=1, max_value=1000, value=115)

# Add user count input
num_activity_users = st.number_input("How many sample users for activity JSON?", min_value=1, max_value=1000, step=50, value=50)

if st.button("📦 Generate Event JSON"):
    if asset_id and api_key:
     products = [
        {"ImageURL": img1, "productURL": url1, "productName": name1, "price": price1},
        {"ImageURL": img2, "productURL": url2, "productName": name2, "price": price2}
    ]

    if "dummy_users" in st.session_state:
        users = random.sample(
            st.session_state["dummy_users"],
            k=min(num_activity_users, len(st.session_state["dummy_users"]))
        )

        event_json = generate_activity_payloads(asset_id, users, products)

        st.success("Sample Event JSON Generated")
        st.json(event_json[:3])  # Preview top 3 only

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
                "Authorization": api_key
            }

            response = requests.post(
                url="https://api.netcorecloud.net/v3/activity/bulk",
                headers=headers,
                json=event_json
            )

            if response.status_code == 200:
                st.success("✅ Data pushed to Netcore successfully!")
            else:
                st.error(f"❌ Failed to push data. Status Code: {response.status_code}")
                st.json(response.json())

    else:
        st.error("⚠️ Please generate dummy users first.")
        st.stop()
else:
    st.error("Please enter Asset ID and API Key first.")
