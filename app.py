import streamlit as st
import requests
import json

# Load API key from Streamlit secrets
API_KEY = st.secrets.get("api_key", "")
MODEL = "x-ai/grok-4.1-fast:free"

st.set_page_config(page_title="Meeting Minutes Extractor", page_icon="📝")
st.title("Meeting Minutes Extractor")
st.write("Paste your meeting transcript and get structured JSON minutes.")

# Text input
transcript = st.text_area("Meeting Transcript", height=300)

# Mock JSON fallback
mock_result = {
    "date": "20th November 2025",
    "attendees": ["Alice", "Bob", "Charlie"],
    "agenda": ["Project updates", "Blockers", "Action items"],
    "discussion": [
        {
            "topic": "Project updates",
            "summary": "Backend API authentication module completed. Data endpoints in progress. Frontend design almost done, waiting for API integration."
        },
        {
            "topic": "Blockers",
            "summary": "No major blockers. Frontend color scheme needs approval."
        }
    ],
    "action_items": [
        {"task": "Finish API endpoints", "owner": "Bob", "deadline": "25th November"},
        {"task": "Integrate frontend with backend", "owner": "Charlie", "deadline": "26th November"},
        {"task": "Review color scheme and provide feedback", "owner": "Alice", "deadline": "22nd November"}
    ]
}

if st.button("Extract Minutes"):
    if not transcript.strip():
        st.warning("Please enter the meeting transcript.")
    else:
        if not API_KEY:
            st.error("API key not found. Please add it to Streamlit secrets as 'api_key'.")
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
                response = requests.post("https://api.openrouter.ai/v1/completions", headers=headers, json=payload, timeout=10)
                response.raise_for_status()
                data = response.json()
                result = data.get("completion") or data.get("output") or "{}"

                # Attempt to parse JSON, fallback to string if parsing fails
                try:
                    st.subheader("Extracted Minutes (JSON)")
                    st.json(json.loads(result))
                except:
                    st.subheader("Extracted Minutes (Raw Text)")
                    st.text(result)

            except requests.exceptions.RequestException as e:
                st.warning(f"Could not reach OpenRouter API. Using mock JSON.\n\nError: {e}")
                st.subheader("Mock Extracted Minutes (JSON)")
                st.json(mock_result)
