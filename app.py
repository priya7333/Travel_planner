import streamlit as st
import requests

# =========================================================
# 🔐 INSERT YOUR SARVAM API KEY BELOW
# =========================================================
SARVAM_API_KEY = "sk_qu4m7nvw_v4P2qUowg5ALmE4MckEYS74s"  # <--- CHANGE THIS ONLY
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
                You are an expert travel planner.
                Write ONLY in {language}.
                Create a {duration}-day itinerary for {destination}.
                Include attractions, food, culture, transport & tips.
                Budget level: {budget}.
                Interests: {', '.join(interests)}.
                Keep it short, clear and structured.
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
                "model": "saarvam-chat",
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 3000
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
# USER INPUT FORM
# -------------------------------------------------------

with st.form("trip_form"):
    destination = st.text_input("Where do you want to go?")
    duration = st.number_input("How many days?", 1, 30, 5)
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

        # 1. Detect language of input
        detected = detect_language(destination)
        detected_lang = detected.get("language", "en")

        # 2. Call Sarvam itinerary generator
        response = generate_itinerary(
            destination, duration, interests, budget, detected_lang
        )

        # 3. Debug panel (shows raw API response)
        st.markdown("### 🛠 DEBUG: API Response")
        st.json(response)

        # 4. Extract content safely
        content = ""
        try:
            content = response["choices"][0]["message"]["content"]
        except:
            content = "⚠️ No content returned from API. Check your API key or model."

        # 5. Translate if needed
        if preferred_lang != "en":
            content = translate_text(content, preferred_lang)

        # 6. Display itinerary
        st.markdown("## 🗺 Your Itinerary")
        st.markdown(content)

# -------------------------------------------------------
# FOOTER
# -------------------------------------------------------

st.markdown("---")
st.markdown("<center>Powered by Sarvam AI</center>", unsafe_allow_html=True)
