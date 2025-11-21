import streamlit as st
import requests
import json
import re
from datetime import datetime

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

# Function to extract date and attendees from transcript
def extract_metadata(transcript_text):
    date_match = re.search(r"Meeting Date:\s*(.*)", transcript_text)
    attendees_match = re.search(r"Attendees:\s*(.*)", transcript_text)
    
    date = date_match.group(1).strip() if date_match else datetime.today().strftime("%d %B %Y")
    attendees = [x.strip() for x in attendees_match.group(1).split(",")] if attendees_match else []
    
    return date, attendees

# Function to call OpenRouter API
def extract_json_from_api(transcript_text):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "input": f"Extract meeting minutes from the following transcript in JSON format with keys: date, attendees, agenda, discussion, action_items:\n\n{transcript_text}"
    }
    try:
        response = requests.post("https://api.openrouter.ai/v1/completions", headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        result = data.get("completion") or data.get("output") or "{}"
        return json.loads(result)
    except Exception as e:
        st.warning(f"Could not reach OpenRouter API. Using mock JSON.\n\nError: {e}")
        # Fill mock JSON with extracted metadata if available
        date, attendees = extract_metadata(transcript_text)
        mock_result_copy = mock_result.copy()
        mock_result_copy["date"] = date
        if attendees:
            mock_result_copy["attendees"] = attendees
        return mock_result_copy

# Button to extract minutes
if st.button("Extract Minutes"):
    if not transcript.strip():
        st.warning("Please enter the meeting transcript.")
    else:
        if not API_KEY:
            st.error("API key not found. Please add it to Streamlit secrets as 'api_key'.")
        else:
            minutes_json = extract_json_from_api(transcript)
            st.subheader("Structured Meeting Minutes (JSON)")
            st.json(minutes_json)
