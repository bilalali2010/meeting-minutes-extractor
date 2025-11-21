import streamlit as st
import re
from datetime import datetime

st.set_page_config(page_title="Meeting Minutes Extractor", page_icon="📝")
st.title("Meeting Minutes Extractor")
st.write("Paste your meeting transcript and get structured JSON minutes (offline, no API required).")

# Input transcript
transcript = st.text_area("Meeting Transcript", height=400)

def extract_date_attendees(text):
    date_match = re.search(r"Meeting Date:\s*(.*)", text)
    attendees_match = re.search(r"Attendees:\s*(.*)", text)
    date = date_match.group(1).strip() if date_match else datetime.today().strftime("%d %B %Y")
    attendees = [x.strip() for x in attendees_match.group(1).split(",")] if attendees_match else []
    return date, attendees

def extract_action_items(text):
    items = []
    # Match patterns like "1. Bob to finish API endpoints by 25th November."
    pattern = re.compile(r"\d+\.\s*(.*?)\s+to\s+(.*?)\s+by\s+(.*?)(?:\.|$)", re.IGNORECASE)
    for match in pattern.finditer(text):
        owner = match.group(1).strip()
        task = match.group(2).strip()
        deadline = match.group(3).strip()
        items.append({"task": task, "owner": owner, "deadline": deadline})
    return items

def extract_discussion(text):
    discussion_dict = {}
    pattern = re.compile(r"(\w+):\s*(.*)")
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        match = pattern.match(line)
        if match:
            speaker, content = match.groups()
            if speaker not in discussion_dict:
                discussion_dict[speaker] = []
            discussion_dict[speaker].append(content)
    # Convert to list of dicts
    discussion_list = []
    for speaker, lines in discussion_dict.items():
        summary = " ".join(lines)
        discussion_list.append({"topic": f"{speaker}'s update", "summary": summary})
    return discussion_list

def extract_agenda(text):
    agenda = []
    # Look for keywords as agenda items
    if re.search(r"project updates", text, re.IGNORECASE):
        agenda.append("Project updates")
    if re.search(r"blockers", text, re.IGNORECASE):
        agenda.append("Blockers")
    if re.search(r"action items", text, re.IGNORECASE):
        agenda.append("Action items")
    return agenda if agenda else ["General Discussion"]

# Button click
if st.button("Extract Minutes"):
    if not transcript.strip():
        st.warning("Please enter the meeting transcript.")
    else:
        date, attendees = extract_date_attendees(transcript)
        agenda = extract_agenda(transcript)
        discussion = extract_discussion(transcript)
        action_items = extract_action_items(transcript)

        minutes_json = {
            "date": date,
            "attendees": attendees,
            "agenda": agenda,
            "discussion": discussion,
            "action_items": action_items
        }

        st.subheader("Structured Meeting Minutes (JSON)")
        st.json(minutes_json)
