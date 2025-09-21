# app.py
import streamlit as st
from transformers import pipeline

# -------------------------
# Load Emotion/ Sentiment Model
# -------------------------
@st.cache_resource
def load_emotion_model():
    return pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base")

emotion_classifier = load_emotion_model()

# -------------------------
# Session State Initialization
# -------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_started" not in st.session_state:
    st.session_state.chat_started = False
if "user_mood" not in st.session_state:
    st.session_state.user_mood = None
if "context" not in st.session_state:
    st.session_state.context = []

# -------------------------
# Landing Page
# -------------------------
st.set_page_config(page_title="LUNAR - Mental Wellness Chatbot", page_icon="🌙")
st.title("🌙 LUNAR")
st.write(
    """
LUNAR is your AI companion for mental wellness. 🌙  
Chat with Luna, share your feelings, and experience empathetic, supportive conversation tailored to your mood.  
Luna adapts to your emotions, helping you move from negative to positive feelings naturally. 💛
"""
)

if not st.session_state.chat_started:
    if st.button("Chat Now"):
        st.session_state.chat_started = True

# -------------------------
# Helper Functions
# -------------------------
def classify_emotion(emotion):
    positive = ["Happy", "Excited", "Relaxed"]
    negative = ["Angry", "Sad", "Anxious", "Stressed", "Lonely", "Bored", "Confused"]
    neutral = ["Neutral"]

    if emotion in positive:
        return "Positive"
    elif emotion in negative:
        return "Negative"
    else:
        return "Neutral"

def get_luna_response(user_msg, sentiment):
    """
    Generate Luna's response based on sentiment AND context.
    """
    st.session_state.context.append((sentiment, user_msg))
    if len(st.session_state.context) > 5:
        st.session_state.context.pop(0)

    prev_negative = any(s == "Negative" for s, _ in st.session_state.context[-3:])

    if sentiment == "Positive":
        responses = [
            "That's great to hear! 😄 What's been the highlight of your day?",
            "I love that! 🌟 Keep spreading the positivity!",
            "Awesome! 😎 Anything fun you did recently?"
        ]
    elif sentiment == "Neutral":
        responses = [
            "I see. How has your day been so far? ☀️",
            "Nice! Did you have anything interesting for lunch today? 🍴",
            "Got it. What are you up to these days? 😌"
        ]
    else:  # Negative
        if prev_negative:
            responses = [
                "I understand. 🌱 Let's try talking about something light. Did you do anything fun recently?",
                "It's okay to feel down sometimes. 💛 Want to share a small positive moment from today?",
                "I hear you. 😔 Let's focus on something that makes you feel a little better."
            ]
        else:
            responses = [
                "I'm here for you. 💛 Want to tell me about something that made you feel that way?",
                "It's okay to feel down sometimes. 🌱 Can we talk about something that makes you feel a little better?",
                "I understand. 😔 Let's try to make the day a bit lighter! What’s one small thing you enjoyed recently?"
            ]

    return responses[len(st.session_state.messages) % len(responses)]

# -------------------------
# Chat Interface
# -------------------------
if st.session_state.chat_started:
    st.subheader("Talk to Luna 💬")

    user_msg = st.text_input("Your Message:")

    # Emotions with emojis
    emotions = [
        "Angry 😡", "Sad 😢", "Anxious 😰", "Happy 😄", "Excited 🤩",
        "Stressed 😓", "Bored 😐", "Lonely 🥺", "Confused 😕", "Relaxed 😌"
    ]
    user_emotion = st.radio("Select your current feeling:", emotions, horizontal=True)

    if st.button("Send") and user_msg.strip():
        selected_emotion_text = user_emotion.split()[0]
        sentiment = classify_emotion(selected_emotion_text)

        # If first negative message, set mood; else shift to General after Luna's first prompt
        if st.session_state.user_mood is None:
            st.session_state.user_mood = sentiment

        # Heading: msg + emotion + sentiment (user mood)
        heading = f"{user_msg} [{selected_emotion_text}] - {st.session_state.user_mood}"
        st.session_state.messages.append(("User", heading))

        # Determine Luna response
        if st.session_state.user_mood == "Negative":
            # First prompt to talk about something better
            luna_response = "It's okay to feel down sometimes. 💛 Let's talk about something better! Can you share a small positive moment from today?"
            st.session_state.user_mood = "General"  # Shift mood to general after first negative response
        else:
            luna_response = get_luna_response(user_msg, sentiment)

        st.session_state.messages.append(("Luna", luna_response))

        # End chat if user types "bye"
        if "bye" in user_msg.lower():
            st.success("Byee 👋 Happy to chat with you! Stay well!")
            st.session_state.chat_started = False
            st.session_state.messages = []
            st.session_state.user_mood = None
            st.session_state.context = []

    # Display chat history
    for sender, message in st.session_state.messages:
        if sender == "User":
            st.markdown(f"**You:** {message}")
        else:
            st.markdown(f"**Luna:** {message}")
