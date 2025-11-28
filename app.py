import streamlit as st
import requests

# =========================================================
# 🔐 INSERT YOUR SARVAM API KEY BELOW
# =========================================================
SARVAM_API_KEY = "PASTE_YOUR_KEY_HERE"  # <--- CHANGE THIS ONLY
# =========================================================

BASE_URL = "https://api.sarvam.ai/v1"

LANGUAGE_CODES = {
    'en': 'en-IN', 'hi': 'hi-IN', 'bn': 'bn-IN',
    'ta': 'ta-IN', 'te': 'te-IN', 'mr': 'mr-IN',
    'gu': 'gu-IN', 'kn': 'kn-IN', 'ml': 'ml-IN',
    'pa': 'pa-IN'
}

# -------------------------------------------------------
# API CALLS
# -------------------------------------------------------

def detect_language(text):
    try:
        res = requests.post(
            f"{BASE_URL}/language/detect",
            headers={
                "Authorization": f"Bearer {SARVAM_API_KEY}",
                "Content-Type": "application/json"
            },
            json={"text": text}
        )
        return res.json()
    except:
        return {"language": "en"}


def translate_text(text, target_lang):
    try:
        res = requests.post(
            "https://api.sarvam.ai/translate",
            headers={
                "api-subscription-key": SARVAM_API_KEY,
                "Content-Type": "application/json"
            },
            json={
                "input": text,
                "source_language_code": "auto",
                "target_language_code": LANGUAGE_CODES.get(target_lang, "en-IN"),
                "mode": "formal",
                "enable_preprocessing": True,
                "output_script": "fully-native",
                "numerals_format": "international"
            }
        )
        return res.json().get("translated_text", text)
    except:
        return text


def generate_itinerary(destination, duration, interests, budget, language):
    try:
        messages = [
            {
                "role": "system",
                "content": f"""
                You are a professional travel planner.
                Respond ONLY in {language}.
                Create a {duration}-day itinerary for {destination}.
                Include attractions, timing, food, culture and travel tips.
                Budget: {budget}. Interests: {', '.join(interests)}.
                Keep it clear and structured.
                """
            },
            {"role": "user", "content": f"Plan my {duration}-day trip to {destination}."}
        ]

        res = requests.post(
            f"{BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {SARVAM_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "sarvam-m",   # ✅ Correct model
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 2000
            }
        )

        return res.json()

    except Exception as e:
        return {"error": str(e)}

# -------------------------------------------------------
# STREAMLIT UI
# -------------------------------------------------------

st.set_page_config(page_title="AI Travel Assistant", page_icon="✈️", layout="wide")

st.title("✈️ AI Travel Assistant")

languages = {
    'en': 'English', 'hi': 'हिंदी', 'bn': 'বাংলা',
    'ta': 'தமிழ்', 'te': 'తెలుగు', 'mr': 'मराठी',
    'gu': 'ગુજરાતી', 'kn': 'ಕನ್ನಡ', 'ml': 'മലയാളം',
    'pa': 'ਪੰਜਾਬੀ'
}

preferred_lang = st.sidebar.selectbox(
    "Choose your preferred language",
    options=list(languages.keys()),
    format_func=lambda x: languages[x]
)

# -------------------------------------------------------
# INPUT FORM
# -------------------------------------------------------

with st.form("trip_form"):
    destination = st.text_input("Where do you want to go?")
    duration = st.number_input("Trip duration (days)", 1, 30, 5)
    interests = st.multiselect(
        "Your interests:",
        ["Culture", "Food", "Nature", "Adventure", "History", "Shopping", "Relaxation"]
    )
    budget = st.select_slider("Budget level", ["Budget", "Moderate", "Luxury"])

    submit = st.form_submit_button("Plan My Trip!")

# -------------------------------------------------------
# PROCESSING
# -------------------------------------------------------

if submit and destination:
    with st.spinner("Generating your itinerary..."):
        
        detected = detect_language(destination)
        detected_lang = detected.get("language", "en")

        response = generate_itinerary(
            destination, duration, interests, budget, detected_lang
        )

        # Debug info
        st.markdown("### 🛠 Debug: API Response")
        st.json(response)

        try:
            content = response["choices"][0]["message"]["content"]
        except:
            content = "⚠️ API returned no content. Check API key or request body."

        if preferred_lang != "en":
            content = translate_text(content, preferred_lang)

        st.markdown("## 🗺 Your Itinerary")
        st.markdown(content)

# -------------------------------------------------------
# FOOTER
# -------------------------------------------------------

st.markdown("---")
st.markdown("<center>Powered by Sarvam AI</center>", unsafe_allow_html=True)
