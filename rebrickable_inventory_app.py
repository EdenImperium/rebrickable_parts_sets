import streamlit as st
import pandas as pd
import requests

# Hardcoded Rebrickable details
USERNAME = "LukeJD"
API_KEY = "c8dbc524c8fc9ef202f39bd1313fad44"
HEADERS = {"Authorization": f"key {API_KEY}"}

PARTS_URL = "https://rebrickable.com/api/v3/lego/sets/{}/parts/?inc_spares=1&page={}"
SET_URL = "https://rebrickable.com/api/v3/lego/sets/{}"

st.title("Rebrickable Set Inventory Exporter (with Spares)")

uploaded_file = st.file_uploader("Upload a CSV with a 'set_id' column", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    if 'set_id' not in df.columns:
        st.error("The uploaded CSV must contain a 'set_id' column.")
    else:
        all_parts = []

        for set_id in df['set_id']:
            # Get set name
            set_info_url = SET_URL.format(set_id)
            set_info_response = requests.get(set_info_url, headers=HEADERS)

            if set_info_response.status_code != 200:
                st.warning(f"Skipping {set_id} (set info not found)")
                continue

            set_name = set_info_response.json().get("name", "Unknown Set")
            st.write(f"Fetching parts for: {set_id} - {set_name}")
            page = 1

            while True:
                parts_url = PARTS_URL.format(set_id, page)
                parts_response = requests.get(parts_url, headers=HEADERS)

                if parts_response.status_code != 200:
                    break

                for part in parts_response.json().get("results", []):
                    all_parts.append({
                        "set_id": set_id,
                        "set_name": set_name,
                        "part_num": part["part"]["part_num"],
                        "part_name": part["part"]["name"],
                        "color_id": part["color"]["id"],
                        "color_name": part["color"]["name"],
                        "quantity": part["quantity"],
                        "is_spare": part["is_spare"]
                    })

                if not parts_response.json().get("next"):
                    break
                page += 1

        result_df = pd.DataFrame(all_parts)
        csv_data = result_df.to_csv(index=False).encode("utf-8")
        st.success("Done! Download your combined inventory below.")
        st.download_button("📦 Download Inventory CSV", csv_data, "inventory_export.csv", "text/csv")
