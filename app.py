import os
import streamlit as st
import pandas as pd
import requests
from dotenv import load_dotenv

# --------------------------
# LOAD ENVIRONMENT VARIABLES
# --------------------------
load_dotenv()
# IMPORTANT: User must put the key in .env — NOT inside the code.
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")

BASE_URL = "https://api.sarvam.ai/v1"

# Language code mapping
LANGUAGE_CODES = {
    'en': 'en-IN',
    'hi': 'hi-IN',
    'bn': 'bn-IN',
    'ta': 'ta-IN',
    'te': 'te-IN',
    'mr': 'mr-IN',
    'gu': 'gu-IN',
    'kn': 'kn-IN',
    'ml': 'ml-IN',
    'pa': 'pa-IN'
}

# --------------------------
# API UTILITY FUNCTIONS
# --------------------------

def detect_language(text):
    """Detect the language of the input text."""
    headers = {
        "Authorization": f"Bearer {SARVAM_API_KEY}",
        "Content-Type": "application/json"
    }
    response = requests.post(
        f"{BASE_URL}/detect-language",
        headers=headers,
        json={"text": text}
    )
    return response.json()

def translate_text(text, target_language, mode="formal"):
    """Translate text using Sarvam's translation API."""
    headers = {
        "api-subscription-key": SARVAM_API_KEY,
        "Content-Type": "application/json"
    }

    target_lang_code = LANGUAGE_CODES.get(target_language, 'en-IN')

    response = requests.post(
        "https://api.sarvam.ai/translate",
        headers=headers,
        json={
            "input": text,
            "source_language_code": "auto",
            "target_language_code": target_lang_code,
            "mode": mode,
            "enable_preprocessing": True,
            "output_script": "fully-native",
            "numerals_format": "international"
        }
    )
    return response.json()

def transliterate_text(text, target_script):
    headers = {
        "Authorization": f"Bearer {SARVAM_API_KEY}",
        "Content-Type": "application/json"
    }
    response = requests.post(
        f"{BASE_URL}/transliterate",
        headers=headers,
        json={"text": text, "target_script": target_script}
    )
    return response.json()

def generate_itinerary(destination, duration, interests, budget, language="en"):
    """Generate travel itinerary using Sarvam Chat Completions."""
    headers = {
        "Authorization": f"Bearer {SARVAM_API_KEY}",
        "Content-Type": "application/json"
    }

    system_prompt = f"""
    You are an expert travel planner specializing in {destination}. 
    Only generate the itinerary in {language}. Avoid English.
    Create a detailed {duration}-day itinerary including:
    - Daily activities with timing
    - Local attractions & hidden gems
    - Cultural experiences
    - Food recommendations
    - Transport tips
    - Budget level: {budget}
    Interests: {', '.join(interests)}
    Make sections short and structured.
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Create a {duration}-day itinerary for {destination}."}
    ]

    response = requests.post(
        f"{BASE_URL}/chat/completions",
        headers=headers,
        json={
            "messages": messages,
            "model": "sarvam-m",
            "temperature": 0.7,
            "max_tokens": 5000
        }
    )

    return response.json()

# --------------------------
# STREAMLIT APP UI
# --------------------------

st.set_page_config(page_title="AI Travel Assistant", page_icon="✈️", layout="wide")

if 'preferred_language' not in st.session_state:
    st.session_state.preferred_language = 'en'

st.title("✈️ AI Travel Assistant")
st.markdown("""
Your personalized travel companion for exploring India and beyond!  
Get customized itineraries, local insights, and cultural guidance in your preferred language.
""")

languages = {
    'en': 'English', 'hi': 'हिंदी', 'bn': 'বাংলা',
    'ta': 'தமிழ்', 'te': 'తెలుగు', 'mr': 'मराठी',
    'gu': 'ગુજરાતી', 'kn': 'ಕನ್ನಡ', 'ml': 'മലയാളം',
    'pa': 'ਪੰਜਾਬੀ'
}

selected_language = st.sidebar.selectbox(
    "Select your preferred language",
    options=list(languages.keys()),
    format_func=lambda x: languages[x]
)

if selected_language != st.session_state.preferred_language:
    st.session_state.preferred_language = selected_language

# --------------------------
# INPUT FORM
# --------------------------

with st.form("travel_planner"):
    col1, col2 = st.columns(2)

    with col1:
        destination = st.text_input("Where would you like to go?")
        travel_dates = st.date_input("When are you planning to travel?")
        duration = st.number_input("How many days?", min_value=1, max_value=30, value=3)

    with col2:
        interests = st.multiselect(
            "What are your interests?",
            ["Culture", "Food", "Nature", "Adventure", "History", "Shopping", "Relaxation"]
        )

        budget = st.select_slider(
            "What's your budget range?",
            options=["Budget", "Moderate", "Luxury"]
        )

    submit_button = st.form_submit_button("Plan My Trip!")

# --------------------------
# PROCESSING
# --------------------------

if submit_button and destination:
    with st.spinner("Creating your personalized itinerary..."):

        lang_detection = detect_language(destination)
        detected_lang = lang_detection.get('language', 'en')

        itinerary_response = generate_itinerary(
            destination, duration, interests, budget, detected_lang
        )

        itinerary = itinerary_response.get('choices', [{}])[0].get('message', {}).get('content', '')

        if st.session_state.preferred_language != 'en':
            translated_itinerary = translate_text(
                itinerary, st.session_state.preferred_language, mode="formal"
            )
            itinerary = translated_itinerary.get('translated_text', itinerary)

        st.markdown("### Your Personalized Itinerary")
        st.markdown(itinerary)

        # Generate travel tips
        tips_response = generate_itinerary(
            destination, 1, ["Practical Tips"], budget, detected_lang
        )

        tips = tips_response.get('choices', [{}])[0].get('message', {}).get('content', '')

        if st.session_state.preferred_language != 'en':
            translated_tips = translate_text(
                tips, st.session_state.preferred_language, mode="formal"
            )
            tips = translated_tips.get('translated_text', tips)

        st.markdown("### Travel Tips")
        st.markdown(tips)

# --------------------------
# FOOTER
# --------------------------

st.markdown("---")
st.markdown(
    "<div style='text-align:center;'>Powered by Sarvam AI | Your trusted travel companion</div>",
    unsafe_allow_html=True
)
