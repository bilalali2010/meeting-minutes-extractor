import streamlit as st
import json
import requests

st.set_page_config(page_title="Meeting Minute Extractor", page_icon="📝")

st.title("📝 Meeting Minute Extractor (JSON Output)")

st.write("You can either paste your meeting notes below or upload a `.txt` file.")

# Text area for pasting notes
meeting_text = st.text_area("Paste Meeting Notes", height=200)

# File uploader
uploaded_file = st.file_uploader("Upload a .txt file", type=["txt"])

if uploaded_file is not None:
    try:
        meeting_text = uploaded_file.read().decode("utf-8")
        st.success("File loaded successfully!")
    except Exception as e:
        st.error(f"Error reading file: {e}")

# Get API key from Streamlit secrets
OPENROUTER_API_KEY = st.secrets["api_key"]

# Function to call OpenRouter AI Grok model
def extract_minutes_grok(text):
    url = "https://api.openrouter.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "x-ai/grok-4.1-fast:free",
        "messages": [
            {
                "role": "user",
                "content": f"""
Extract key points, action items, decisions, and participants from the following meeting notes.
Format the output strictly in JSON with keys: "participants", "summary", "action_items", "decisions".

Meeting Notes:
{text}
"""
            }
        ],
        "temperature": 0.2,
        "max_tokens": 500
    }

    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        output_text = response.json()["choices"][0]["message"]["content"].strip()
        try:
            return json.loads(output_text)
        except:
            # Fixed syntax error here
            return {
                "error": "Failed to parse JSON",
                "raw_output": output_text
            }
    else:
        return {
            "error": f"API request failed with status {response.status_code}",
            "details": response.text
        }


# Trigger extraction
if st.button("Extract Meeting Minutes"):
    if not meeting_text:
        st.warning("Please paste notes or upload a file.")
    else:
        with st.spinner("Extracting..."):
            result = extract_minutes_grok(meeting_text)
            st.subheader("JSON Output")
            st.json(result)

            # Download JSON
            st.download_button(
                label="Download JSON",
                data=json.dumps(result, indent=4),
                file_name="meeting_minutes.json",
                mime="application/json"
            )
