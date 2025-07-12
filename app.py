import streamlit as st
import requests
import qrcode
from PIL import Image
import io
from openai import OpenAI

# 🔐 OpenAI setup (dummy key, replace with yours securely)
client = OpenAI(api_key="sk-your-key")

# ✅ MUST initialize session state at the top
if "run_doctor_search" not in st.session_state:
    st.session_state["run_doctor_search"] = False

# 🎨 Page setup
st.set_page_config(page_title="NM2TECH Doctor Network", page_icon="🏥", layout="centered")
st.header("🏥 NM2TECH Doctor Network")
st.markdown("Find doctors based on your location and specialty — powered by NPI Registry and AI assistant.")
st.markdown("---")
st.markdown("## 🩺 Doctor Network Search")

# 🎯 User Inputs
location = st.text_input("Enter City or ZIP Code")
specialty_options = [
    "Family Medicine", "Cardiology", "Dermatology", "Pediatrics",
    "Oncology", "General Practice", "Other"
]
specialty = st.selectbox("Select Specialty", specialty_options)
limit = st.slider("Number of results", 3, 10, 5)  # 🚫 DO NOT assign key="run_doctor_search" here

# 🔍 Button
if st.button("🔍 Find Doctors"):
    st.session_state["run_doctor_search"] = True

# 🔎 Run Search
if st.session_state["run_doctor_search"]:
    with st.spinner("Searching NPI Registry..."):
        taxonomy_map = {
            "Family Medicine": "207Q00000X",
            "Cardiology": "207RC0000X",
            "Dermatology": "207N00000X",
            "Pediatrics": "208000000X",
            "Oncology": "208D00000X",
            "General Practice": "208D00000X"
        }

        taxonomy_code = taxonomy_map.get(specialty)
        url = "https://npiregistry.cms.hhs.gov/api/"
        params = {
            "version": "2.1",
            "limit": limit,
            "city": location if location and not location.isnumeric() else None,
            "postal_code": location if location and location.isnumeric() else None,
            "taxonomy": taxonomy_code,
            "enumeration_type": "NPI-1"
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            results = data.get("results", [])

            if not results:
                st.warning("No providers found — try changing location or specialty.")
            else:
                st.markdown("### 🔎 Matching Providers")
                for p in results:
                    basic = p.get("basic", {})
                    addresses = p.get("addresses", [])
                    address = addresses[0] if addresses else {}

                    name = f"{basic.get('first_name', '')} {basic.get('last_name', '')}".strip()
                    phone = address.get("telephone_number", "Not listed")
                    addr_1 = address.get("address_1", "")
                    city = address.get("city", "")
                    state = address.get("state", "")
                    zip_code = address.get("postal_code", "")
                    full_address = f"{addr_1}, {city}, {state} {zip_code}".strip()

                    map_link = f"https://www.google.com/maps/search/?api=1&query={full_address.replace(' ', '+')}"
                    qr_img = qrcode.make(map_link)
                    qr_img = qr_img.resize((130, 130))
                    buf = io.BytesIO()
                    qr_img.save(buf, format="PNG")
                    qr_bytes = buf.getvalue()

                    st.subheader(f"👨‍⚕️ {name} – {specialty}")
                    st.markdown(f"""
                    📍 {full_address}  
                    📞 `{phone}`  
                    🗺️ [View Location]({map_link})
                    """)
                    st.image(qr_bytes, caption="📱 Scan to open map", use_container_width=False)
                    st.markdown("---")

        except Exception as e:
            st.error(f"Error occurred: {e}")

    # Reset trigger
    st.session_state["run_doctor_search"] = False
