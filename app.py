import streamlit as st
import json
import requests

st.set_page_config(page_title="Meeting Minute Extractor", page_icon="📝")

st.title("📝 Meeting Minute Extractor (JSON Output)")

st.write("Paste your meeting notes/transcript below:")

meeting_text = st.text_area("Meeting Notes", height=300)

# Get API key from Streamlit secrets
OPENROUTER_API_KEY = st.secrets["openrouter"]["api_key"]

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
            return {"error": "Failed to parse JSON. Raw output": output_text}
    else:
        return {"error": f"API request failed with status {response.status_code}", "details": response.text}


if st.button("Extract Meeting Minutes"):
    if not meeting_text:
        st.warning("Please enter meeting notes.")
    else:
        with st.spinner("Extracting..."):
            result = extract_minutes_grok(meeting_text)
            st.subheader("JSON Output")
            st.json(result)

            # Download button
            st.download_button(
                label="Download JSON",
                data=json.dumps(result, indent=4),
                file_name="meeting_minutes.json",
                mime="application/json"
            )
