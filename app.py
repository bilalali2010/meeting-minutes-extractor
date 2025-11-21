import streamlit as st
import requests
import json
import os

# Load API key from Streamlit secrets
API_KEY = st.secrets["api_key"]
MODEL = "x-ai/grok-4.1-fast:free"

st.set_page_config(page_title="Meeting Minutes Extractor", page_icon="📝")

st.title("Meeting Minutes Extractor")
st.write("Paste your meeting transcript and get structured JSON minutes.")

# Text input
transcript = st.text_area("Meeting Transcript", height=300)

if st.button("Extract Minutes"):
    if not transcript.strip():
        st.warning("Please enter the meeting transcript.")
    else:
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": MODEL,
            "input": f"Extract meeting minutes from the following transcript in JSON format:\n\n{transcript}"
        }

        try:
            response = requests.post("https://api.openrouter.ai/v1/completions", headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            # Grok usually returns output text in `completion` or `output` field
            result = data.get("completion") or data.get("output") or "No result found"
            
            # Display as JSON
            st.subheader("Extracted Minutes (JSON)")
            try:
                st.json(json.loads(result))
            except:
                st.text(result)
        except Exception as e:
            st.error(f"Error: {e}")
