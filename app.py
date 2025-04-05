import streamlit as st
import requests
import json
import time
import logging

# Set page configuration
st.set_page_config(
    page_title="🎵 AI Lyrics Generator",
    page_icon="🎤",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Spotify-inspired CSS
st.markdown("""
<style>
    :root {
        --spotify-green: #1DB954;
        --spotify-black: #191414;
        --spotify-white: #FFFFFF;
        --spotify-gray: #B3B3B3;
    }

    .stApp {
        background-color: var(--spotify-black);
        color: var(--spotify-white);
    }

    .stSidebar {
        background-color: #000000 !important;
        border-right: 1px solid #282828 !important;
    }

    .lyrics-card {
        background: #181818;
        border-radius: 8px;
        padding: 25px;
        margin: 20px 0;
        border-left: 4px solid var(--spotify-green);
    }

    .stTextInput>div>div>input {
        background: #2A2A2A !important;
        color: var(--spotify-white) !important;
        border: 1px solid #404040 !important;
        border-radius: 20px !important;
    }

    .stButton>button {
        background: var(--spotify-green) !important;
        color: var(--spotify-black) !important;
        border: none !important;
        border-radius: 20px !important;
        padding: 10px 30px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }

    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 2px 8px rgba(29, 185, 84, 0.3);
    }

    .genre-pill {
        background: #404040;
        color: var(--spotify-white);
        padding: 6px 15px;
        border-radius: 20px;
        margin: 5px;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize session state
if "lyrics_history" not in st.session_state:
    st.session_state.lyrics_history = []

# Sidebar - Settings
with st.sidebar:
    st.title("⚙️ Generator Settings")
    api_key = st.text_input("OpenRouter API Key", type="password")
    st.markdown("[Get API Key](https://openrouter.ai/keys)")
    
    genre = st.selectbox(
        "🎸 Music Genre",
        ["Pop", "Rock", "Hip-Hop", "Country", "Electronic", "R&B"]
    )
    
    mood = st.select_slider(
        "🎭 Song Mood",
        options=["😭 Sad", "😐 Neutral", "😊 Happy", "🔥 Energetic", "💔 Heartbreak"]
    )
    
    creativity = st.slider(
        "🎨 Creativity Level",
        0.0, 1.0, 0.7
    )
    
    if st.button("🧹 Clear History"):
        st.session_state.lyrics_history = []

# Main Interface
st.title("🎤 AI Lyrics Composer")
st.caption("Craft perfect song lyrics powered by AI")

# Input Section
theme = st.text_input("🎹 Enter your song theme or keywords")
generate_button = st.button("🎧 Generate Lyrics")

# Lyrics Display
for lyrics in st.session_state.lyrics_history:
    with st.container():
        st.markdown(f"""
        <div class='lyrics-card'>
            <div style='color: var(--spotify-green); margin-bottom: 15px;'>
                🎶 {lyrics['theme']} • {lyrics['genre']} • {lyrics['mood']}
            </div>
            <pre style='white-space: pre-wrap; font-family: inherit;'>{lyrics['content']}</pre>
        </div>
        """, unsafe_allow_html=True)

# Generation Logic
if generate_button:
    if not api_key:
        st.error("🔑 API key required! Check sidebar settings")
        st.stop()
    
    if not theme:
        st.warning("🎵 Please enter a song theme or keywords")
        st.stop()
    
    with st.spinner("🎵 Composing your lyrics..."):
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://lyrics-generator.streamlit.app",
                    "X-Title": "AI Lyrics Generator"
                },
                json={
                    "model": "google/palm-2-chat-bison",
                    "messages": [{
                        "role": "system",
                        "content": f"""You are a professional songwriter. Create lyrics with:
1. Verse-Chorus structure
2. {genre} genre style
3. {mood} mood
4. Theme: {theme}
5. Use poetic devices (metaphors, rhyme)
6. Add section headers like [Verse 1], [Chorus]
7. Never use markdown"""
                    }],
                    "temperature": creativity,
                    "max_tokens": 500
                },
                timeout=30
            )

            if response.status_code == 200:
                lyrics_content = response.json()['choices'][0]['message']['content']
                
                # Store in history
                st.session_state.lyrics_history.insert(0, {
                    "theme": theme,
                    "genre": genre,
                    "mood": mood,
                    "content": lyrics_content
                })
                
                # Display new lyrics
                with st.container():
                    st.markdown(f"""
                    <div class='lyrics-card'>
                        <div style='color: var(--spotify-green); margin-bottom: 15px;'>
                            🎶 {theme} • {genre} • {mood}
                        </div>
                        <pre style='white-space: pre-wrap; font-family: inherit;'>{lyrics_content}</pre>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.error("🎼 Failed to generate lyrics. Please try again.")
                
        except Exception as e:
            st.error(f"🎹 Error: {str(e)}")