from event_generator import generate_activity_payloads
import streamlit as st
import pandas as pd
from faker import Faker
import random
import requests
from datetime import datetime

fake = Faker()

st.set_page_config(page_title="Netcore Dummy Data Generator", layout="wide")
st.title("📧 Netcore Dummy Contact Generator")

# Step 1: Generate Dummy Users
num_users = st.number_input(
    "How many users to generate?",
    min_value=100, max_value=30000, step=1000, value=1000
)

custom_attr_1 = st.text_input("Custom Attribute 1 Name (e.g., SEGMENT)", value="SEGMENT")
custom_values_1 = st.text_input("Possible values for Attribute 1 (comma separated)", value="NEW,LOYAL,VIP")

custom_attr_2 = st.text_input("Custom Attribute 2 Name (e.g., TIER)", value="TIER")
custom_values_2 = st.text_input("Possible values for Attribute 2 (comma separated)", value="BRONZE,SILVER,GOLD")

website = st.text_input("Enter website/brand (e.g., shop.example.com)", value="shop.example.com")
asset_id = st.text_input("Enter Netcore Asset ID", value="12345")
api_key = st.text_input("Enter Netcore API Key", type="password", value="your_api_key_here")

generate = st.button("🚀 Generate Dummy Users")

if generate:
    emails = [f"user{i}@example.com" for i in range(1, num_users + 1)]
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

    st.session_state["dummy_users"] = emails
    st.success("Dummy contact list generated ✅")
    st.write(df.head(10))

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name='dummy_contact_list.csv',
        mime='text/csv'
    )
    st.markdown("""
    ### ℹ️ Next Steps in the Panel
    1. **Download this data** using the button above.  
    2. **Create attributes in the panel** corresponding to the columns you see here (EMAIL, PHONE, LANGUAGE, etc.).  
    3. **Upload the data** into the panel.  
    4. You might receive a **harvest error** — if you do, please reach out to Support.  
    5. Only after completing these steps, proceed to **generate and push event data**.  
    """)


# Step 2: Product + Activity Payload
st.header("🧪 Generate Product Activity Event JSON")

col1, col2 = st.columns(2)
with col1:
    img1 = st.text_input("Product 1 Image URL", value="https://via.placeholder.com/150")
    url1 = st.text_input("Product 1 Product URL", value="https://shop.example.com/product1")
    name1 = st.text_input("Product 1 Name", value="Cool Shirt")
    price1 = st.number_input("Product 1 Price", min_value=1, max_value=1000, value=79)

with col2:
    img2 = st.text_input("Product 2 Image URL", value="https://via.placeholder.com/200")
    url2 = st.text_input("Product 2 Product URL", value="https://shop.example.com/product2")
    name2 = st.text_input("Product 2 Name", value="Trendy Shoes")
    price2 = st.number_input("Product 2 Price", min_value=1, max_value=1000, value=115)

num_activity_users = st.number_input(
    "How many users for activity JSON?",
    min_value=1, max_value=1000, step=50, value=50
)

# ✅ Generate Event JSON
if st.button("📦 Generate Event JSON"):
    if not asset_id or not api_key:
        st.error("Please enter Asset ID and API Key first.")
        st.stop()

    if "dummy_users" not in st.session_state:
        st.error("⚠️ Please generate dummy users first.")
        st.stop()

    products = [
        {"ImageURL": img1, "productURL": url1, "productName": name1, "price": price1, "currency": "$"},
        {"ImageURL": img2, "productURL": url2, "productName": name2, "price": price2, "currency": "$"}
    ]

    selected_users = random.sample(
        st.session_state["dummy_users"],
        k=min(num_activity_users, len(st.session_state["dummy_users"]))
    )

    event_json = []
    for user in selected_users:
        product = random.choice(products)
        event = {
            "asset_id": asset_id,
            "activity_name": "Product Purchase",
            "timestamp": datetime.utcnow().isoformat(),
            "identity": user,
            "activity_source": "web",
            "activity_params": product
        }
        event_json.append(event)

    st.session_state["event_json"] = event_json  # ✅ Save for push
    st.success("Sample Event JSON Generated ✅")
    st.json(event_json[:3])

    json_str = str(event_json).replace("'", '"')
    st.download_button(
        label="📥 Download JSON",
        data=json_str,
        file_name="sample_event_payloads.json",
        mime="application/json"
    )

# ✅ Push to Netcore (separate button)
if st.button("🚀 Push to Netcore"):
    if "event_json" not in st.session_state:
        st.error("⚠️ Please generate events first.")
    else:
        full_url = "https://api2.netcoresmartech.com/v1/activity/upload"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        try:
            response = requests.post(
                url=full_url,
                headers=headers,
                json=st.session_state["event_json"],
                timeout=15
            )

            st.write("➡️ Request URL:", full_url)
            st.write("➡️ Sending Payload (first 1 event):")
            st.json(st.session_state["event_json"][:1])

            if response.status_code == 200:
                st.success("✅ Data pushed to Netcore successfully!")
                try:
                    st.json(response.json())
                except:
                    st.write(response.text)
            else:
                st.error(f"❌ Failed with status code: {response.status_code}")
                try:
                    st.json(response.json())
                except:
                    st.write(response.text)

        except Exception as e:
            st.error(f"🚨 Request failed: {str(e)}")
