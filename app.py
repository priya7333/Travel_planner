import os
import streamlit as st
import requests

# =========================================================
# 🔐 INSERT YOUR API KEY BELOW (replace YOUR_KEY_HERE)
# =========================================================
SARVAM_API_KEY = "sk_qu4m7nvw_v4P2qUowg5ALmE4MckEYS74s"   # ←←← REPLACE THIS ONLY
# =========================================================

BASE_URL = "https://api.sarvam.ai/v1"

LANGUAGE_CODES = {
    'en': 'en-IN', 'hi': 'hi-IN', 'bn': 'bn-IN',
    'ta': 'ta-IN', 'te': 'te-IN', 'mr': 'mr-IN',
    'gu': 'gu-IN', 'kn': 'kn-IN', 'ml': 'ml-IN', 'pa': 'pa-IN'
}

# --------------------------
# API UTILITIES
# --------------------------

def detect_language(text):
    """Detect language safely."""
    try:
        headers = {
            "Authorization": f"Bearer {SARVAM_API_KEY}",
            "Content-Type": "application/json"
        }
        response = requests.post(
            f"{BASE_URL}/language/detect",
            headers=headers,
            json={"text": text}
        )
        return response.json()
    except Exception as e:
        return {"language": "en", "error": str(e)}


def translate_text(text, target_language, mode="formal"):
    try:
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
    except:
        return {"translated_text": text}


def generate_itinerary(destination, duration, interests, budget, language="en"):
    """Generate plan using Sarvam chat model."""
    if not language:
        language = "en"

    try:
        headers = {
            "Authorization": f"Bearer {SARVAM_API_KEY}",
            "Content-Type": "application/json"
        }

        system_prompt = f"""
        You are an expert travel planner for {destination}.
        Write the itinerary ONLY in {language}.
        Create a {duration}-day itinerary with:
        - Activities
        - Local attractions
        - Culture, food
        - Transport tips
        - Budget: {budget}
        Interests: {', '.join(interests)}
        Keep it structured and concise.
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
                "model": "saarvam-chat",
                "temperature": 0.7,
                "max_tokens": 4000
            }
        )

        return response.json()

    except Exception as e:
        return {"choices": [{"message": {"content": f"Error: {str(e)}"}}]}


# --------------------------
# STREAMLIT UI
# --------------------------

st.set_page_config(page_title="AI Travel Assistant", page_icon="✈️", layout="wide")

if 'preferred_language' not in st.session_state:
    st.session_state.preferred_language = 'en'

st.title("✈️ AI Travel Assistant")
st.markdown("Your smart travel planner for India and worldwide.")

languages = {
    'en': 'English', 'hi': 'हिंदी', 'bn': 'বাংলা',
    'ta': 'தமிழ்', 'te': 'తెలుగు', 'mr': 'मराठी',
    'gu': 'ગુજરાતી', 'kn': 'ಕನ್ನಡ', 'ml': 'മലയാളം',
    'pa': 'ਪੰਜਾਬੀ'
}

selected_language = st.sidebar.selectbox(
    "Choose your preferred language",
    options=list(languages.keys()),
    format_func=lambda x: languages[x]
)

st.session_state.preferred_language = selected_language

# --------------------------
# FORM
# --------------------------

with st.form("trip_form"):
    col1, col2 = st.columns(2)

    with col1:
        destination = st.text_input("Where do you want to go?")
        travel_dates = st.date_input("Travel dates")
        duration = st.number_input("Trip duration (days)", 1, 30, 3)

    with col2:
        interests = st.multiselect(
            "Select interests",
            ["Culture", "Food", "Nature", "Adventure", "History", "Shopping", "Relaxation"]
        )
        budget = st.select_slider("Budget", ["Budget", "Moderate", "Luxury"])

    submitted = st.form_submit_button("Plan My Trip!")

# --------------------------
# ACTION
# --------------------------

if submitted and destination:
    with st.spinner("Planning your perfect trip..."):

        detected = detect_language(destination)
        lang = detected.get("language", "en")

        itinerary_response = generate_itinerary(
            destination=destination,
            duration=duration,
            interests=interests,
            budget=budget,
            language=lang
        )

        content = itinerary_response.get("choices", [{}])[0].get("message", {}).get("content", "")

        if st.session_state.preferred_language != "en":
            translated = translate_text(content, st.session_state.preferred_language)
            content = translated.get("translated_text", content)

        st.markdown("## 🗺 Your Itinerary")
        st.markdown(content)


st.markdown("---")
st.markdown("<center>Powered by Sarvam AI</center>", unsafe_allow_html=True)
