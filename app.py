import streamlit as st
import requests
import json
from datetime import datetime
from typing import Dict, List, Optional

from prompts import get_prompt_template, FARMING_TOPICS_EXAMPLES
from utils import (
    format_markdown_response,
    export_to_markdown,
    extract_checklist_items,
    validate_api_key_format,
    estimate_tokens
)
from config import Config

# Page Configuration
st.set_page_config(
    page_title="AgriSmart – AI Farming Advisor",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown(Config.CSS_STYLE, unsafe_allow_html=True)


# Initialize Session State
def init_session_state():
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    if 'farmer_profile' not in st.session_state:
        st.session_state.farmer_profile = {}
    if 'checklists' not in st.session_state:
        st.session_state.checklists = {}
    if 'api_calls_count' not in st.session_state:
        st.session_state.api_calls_count = 0
    if 'total_tokens_used' not in st.session_state:
        st.session_state.total_tokens_used = 0

init_session_state()


# API Call Function
def call_openrouter_api(
    prompt: str,
    api_key: str,
    model: str = "openai/gpt-4o-mini",
    max_tokens: int = 2000,
    stream: bool = True,
    context: Optional[List[Dict]] = None
) -> Optional[str]:

    API_URL = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Build message stack
    messages = [
        {"role": "system", "content": Config.SYSTEM_INSTRUCTIONS}
    ]

    # Add history for context
    if context:
        messages.extend(context[-6:])

    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
        "top_p": 0.9,
        "max_tokens": max_tokens,
        "stream": stream
    }

    try:
        if stream:
            response = requests.post(API_URL, headers=headers, json=payload, stream=True)

            if response.status_code != 200:
                st.error(f"API Error: {response.status_code} — {response.text}")
                return None

            full_response = ""
            response_placeholder = st.empty()

            for line in response.iter_lines():
                if line:
                    decoded = line.decode('utf-8')
                    if decoded.startswith("data: "):
                        decoded = decoded[6:]

                        if decoded.strip() == "[DONE]":
                            break

                        try:
                            chunk = json.loads(decoded)

                            if "choices" in chunk:
                                delta = chunk["choices"][0].get("delta", {})
                                content = delta.get("content", "")
                                full_response += content
                                response_placeholder.markdown(full_response + "▌")
                        except:
                            continue

            response_placeholder.markdown(full_response)
            return full_response

        else:
            response = requests.post(API_URL, headers=headers, json=payload)
            return response.json()["choices"][0]["message"]["content"]

    except Exception as e:
        st.error(f"Error communicating with API: {str(e)}")
        return None


# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/external-flatart-icons-outline-flatarticons/64/4a90e2/external-farm-smart-farming-flatart-icons-outline-flatarticons.png", width=80)
    st.markdown("## 🔧 Configuration")

    api_key = st.text_input(
        "OpenRouter API Key",
        type="password",
        help="Get your key from https://openrouter.ai/keys"
    )

    if api_key and not validate_api_key_format(api_key):
        st.warning("⚠️ API key seems invalid")

    model_choice = st.selectbox(
        "AI Model",
        ["openai/gpt-4o-mini", "openai/gpt-4o", "anthropic/claude-3-5-sonnet", "google/gemini-pro"]
    )

    with st.expander("⚙️ Advanced Settings"):
        enable_streaming = st.checkbox("Enable Streaming", True)
        max_tokens = st.slider("Max Tokens", 500, 3000, 2000, 100)
        include_context = st.checkbox("Use Conversation Context", True)

    st.markdown("---")
    st.markdown("## 👨‍🌾 Farmer Profile")

    with st.form("profile_form"):
        farm_location = st.text_input("Farm Location (City / Village)")
        farm_size = st.text_input("Farm Size (acres/hectares)")
        crop_type = st.text_input("Primary Crop")
        soil_type = st.selectbox("Soil Type", ["Alluvial", "Black", "Red", "Sandy", "Clay", "Loamy", "Unknown"])

        if st.form_submit_button("Save Profile"):
            st.session_state.farmer_profile = {
                "location": farm_location,
                "farm_size": farm_size,
                "crop_type": crop_type,
                "soil_type": soil_type,
                "updated": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            st.success("Profile saved!")

    # Stats
    st.markdown("---")
    st.metric("API Calls", st.session_state.api_calls_count)
    st.metric("Tokens Used", f"{st.session_state.total_tokens_used:,}")

    if st.button("Clear History", use_container_width=True):
        st.session_state.conversation_history = []
        st.session_state.checklists = {}
        st.rerun()


# Main UI
st.markdown('<h1 class="main-header">🌾 AgriSmart – AI Farming Advisor</h1>', unsafe_allow_html=True)
st.markdown("Get AI-powered insights for crops, soil, irrigation, pests, and overall farm productivity.")

# Topic selection
topic_map = {
    "🌱 Crop Guidance": "crops",
    "🌾 Soil & Fertility": "soil",
    "🐛 Pest Diagnosis": "pests",
    "💧 Irrigation Planning": "irrigation",
    "🌦 Weather & Climate Impact": "weather",
    "📈 Yield Optimization": "yield",
    "📦 Market Prices": "market",
    "📚 General Advice": "general"
}

st.markdown("### Select Topic")
col1, col2 = st.columns([2, 1])

with col1:
    topic_display = st.selectbox("Choose a farming topic:", list(topic_map.keys()))
    topic = topic_map[topic_display]

with col2:
    if topic in FARMING_TOPICS_EXAMPLES:
        st.markdown("**Examples:**")
        for ex in FARMING_TOPICS_EXAMPLES[topic][:2]:
            if st.button(ex[:30] + "...", key=ex, use_container_width=True):
                st.session_state.quick_query = ex

# Query Box
st.markdown("### Ask Your Farming Question")

default_query = st.session_state.get("quick_query", "")
query = st.text_area(
    "Describe your question:",
    value=default_query,
    height=120,
    placeholder="Example: How to improve yield for tomato crop during winter?"
)

if "quick_query" in st.session_state:
    del st.session_state.quick_query


# Buttons
colA, colB, colC = st.columns(3)
generate = colA.button("Get Advice", type="primary")
simplify = colB.button("Simplify")
expand = colC.button("Expand")


# Process Query
if any([generate, simplify, expand]):
    if not query:
        st.error("Please enter a question.")
    elif not api_key:
        st.error("Please enter your API key.")
    else:
        modifier = ""
        if simplify:
            modifier = "\n\nSimplify the previous response for a farmer with limited technical knowledge."
        if expand:
            modifier = "\n\nExpand the previous response with more scientific explanation and case studies."

        # Profile context
        profile = st.session_state.farmer_profile
        profile_context = ""
        if profile:
            profile_context = (
                f"\n\nFarmer Profile:\n"
                f"- Location: {profile['location']}\n"
                f"- Farm Size: {profile['farm_size']}\n"
                f"- Crop: {profile['crop_type']}\n"
                f"- Soil Type: {profile['soil_type']}\n"
            )

        # Build final prompt
        prompt_template = get_prompt_template(topic)
        final_prompt = prompt_template.format(query=query) + profile_context + modifier

        # Context history
        history_context = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in st.session_state.conversation_history[-6:]
        ] if include_context else None

        with st.spinner("Thinking..."):
            st.markdown("---")
            st.markdown(f"## 🌾 Advice on {topic_display}")

            response = call_openrouter_api(
                prompt=final_prompt,
                api_key=api_key,
                model=model_choice,
                max_tokens=max_tokens,
                stream=enable_streaming,
                context=history_context
            )

            if response:
                st.session_state.api_calls_count += 1
                st.session_state.total_tokens_used += estimate_tokens(final_prompt + response)

                # Save history
                st.session_state.conversation_history.append({"role": "user", "content": query})
                st.session_state.conversation_history.append({"role": "assistant", "content": response})

                # Checklist extraction
                checklist = extract_checklist_items(response)

                if checklist:
                    st.markdown("### ✔️ Action Steps")
                    checklist_key = f"{topic}_{len(st.session_state.conversation_history)}"

                    if checklist_key not in st.session_state.checklists:
                        st.session_state.checklists[checklist_key] = [False] * len(checklist)

                    for i, item in enumerate(checklist):
                        state = st.checkbox(
                            item,
                            value=st.session_state.checklists[checklist_key][i],
                            key=f"{checklist_key}_{i}"
                        )
                        st.session_state.checklists[checklist_key][i] = state

                    completed = sum(st.session_state.checklists[checklist_key])
                    total = len(checklist)
                    st.progress(completed / total)

                # Exports
                st.markdown("---")
                md_data = export_to_markdown(query, response, topic_display, checklist)
                st.download_button(
                    label="📥 Download as Markdown",
                    data=md_data,
                    file_name="agrisMart_response.md",
                    mime="text/markdown"
                )


# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align:center;color:gray;padding:1rem'>
        🌾 Built with ❤️ | AgriSmart AI | Powered by OpenRouter
    </div>
    """,
    unsafe_allow_html=True
)
