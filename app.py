import streamlit as st 
from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.duckduckgo import DuckDuckGo
import google.generativeai as genai

import time
from dotenv import load_dotenv
load_dotenv()

import os

API_KEY = os.getenv("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

# Page configuration
st.set_page_config(
    page_title="Multimodal AI Agent - Video Summarizer",
    page_icon="🎥",
    layout="wide"
)

st.title("Phidata Video AI Summarizer Agent 🎥🎤🖬")
st.header("Powered by Gemini 2.0 Flash Exp")

@st.cache_resource
def initialize_agent():
    return Agent(
        name="Video AI Summarizer",
        model=Gemini(id="gemini-2.0-flash-exp"),
        tools=[DuckDuckGo()],
        markdown=True,
    )

# Initialize the agent
multimodal_Agent = initialize_agent()

# Initialize session state variables
if "selected_video" not in st.session_state:
    st.session_state.selected_video = None
if "video_options" not in st.session_state:
    st.session_state.video_options = []
if "video_searched" not in st.session_state:
    st.session_state.video_searched = False

# User input to fetch a video
video_query = st.text_input(
    "Enter search keywords for the video you want to summarize",
    placeholder="Example: 'Latest AI advancements TED Talk'",
    help="The AI agent will search for a relevant video and summarize it."
)

if st.button("🔍 Search for Videos", key="search_video_button"):
    if not video_query:
        st.warning("Please enter a search query to find a video.")
    else:
        try:
            with st.spinner("Searching for relevant videos..."):
                search_prompt = f"Find relevant videos on '{video_query}'. Provide a list of informative latest YouTube or other video links with their titles. Add the link at the end of the string to ease the capture of the link using the code(selected_video.split(' ')[-1])"
                search_result = multimodal_Agent.run(search_prompt)
                st.session_state.video_options = search_result.content.strip().split('\n')
                st.session_state.video_searched = True  # Set flag to show dropdown

        except Exception as error:
            st.error(f"An error occurred: {error}")

# Step 2: Show video selection dropdown only after search
if st.session_state.video_searched and st.session_state.video_options:
    selected_video = st.selectbox("Select a video to analyze:", st.session_state.video_options)
    
    if st.button("🎥 Confirm Video Selection"):
        st.session_state.selected_video = selected_video.split(' ')[-1]  # Extracting the URL

# Step 3: Show video and analysis input only after confirmation
if st.session_state.selected_video:
    video_url = st.session_state.selected_video
    st.video(video_url)
    
    user_query = st.text_area(
        "What insights are you seeking from the video?",
        placeholder="Ask anything about the video content. The AI agent will analyze it.",
        help="Provide specific questions or insights you want from the video."
    )
    
    if st.button("📜 Summarize Video", key="summarize_video_button"):
        if not user_query:
            st.warning("Please enter a question or insight to analyze the video.")
        else:
            with st.spinner("Processing video and generating summary..."):
                analysis_prompt = (
                    f"""
                    Analyze the video available at {video_url}.
                    Respond to the following query using video insights and supplementary web research:
                    {user_query}

                    Provide a detailed, user-friendly, and actionable response.
                    """
                )
                response = multimodal_Agent.run(analysis_prompt)
            
            st.subheader("Analysis Result")
            st.markdown(response.content)
            
