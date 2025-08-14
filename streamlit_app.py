import streamlit as st
import random
import time
import requests
import json
from huggingface_hub import HfApi, InferenceClient
import os

# Initialize session state
if 'session_started' not in st.session_state:
    st.session_state.session_started = False
if 'current_question' not in st.session_state:
    st.session_state.current_question = ""
if 'recorded_response' not in st.session_state:
    st.session_state.recorded_response = ""
if 'is_recording' not in st.session_state:
    st.session_state.is_recording = False

# Initialize Hugging Face API
@st.cache_resource
def get_hf_client():
    TOKEN = "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"
    return InferenceClient(token=TOKEN)

def generate_question_with_hf():
    """Generate a question using Hugging Face model"""
    try:
        client = get_hf_client()
        
        # Prompt for question generation
        topics = [
            "leadership and teamwork",
            "problem solving skills", 
            "career goals and motivation",
            "technical skills and experience",
            "communication and interpersonal skills",
            "work ethic and reliability",
            "adaptability and learning",
            "conflict resolution",
            "project management",
            "innovation and creativity"
        ]
        
        selected_topic = random.choice(topics)
        prompt = f"Generate an interview question about {selected_topic}. Make it a clear, professional question and generate only the question."
        
        # Generate question using the model
        completion = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3-0324",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
        )
        
        # Extract the generated question
        question = completion.choices[0].message.content.strip()
        
        # Check if the response is valid
        if not question or len(question) < 10:
            raise Exception("Generated response is too short or empty")
            
        if not question.endswith('?'):
            question += '?'
            
        return question
        
    except Exception as e:
        st.error(f"❌ Failed to generate AI question: {str(e)}")
        return None

# Main app logic
if not st.session_state.session_started:
    # Welcome page with Start Session button
    st.title("🤖 AI-Powered Interview Practice App")
    st.write("Practice with dynamically generated questions using Hugging Face AI models!")
    
    if st.button("Start Session", type="primary", use_container_width=True):
        st.session_state.session_started = True
        st.session_state.current_question = generate_question_with_hf()
        st.rerun()

else:
    # Question page (after session starts)
    st.title("🤖 AI-Generated Interview Question")
    
    # Back button
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("← Back"):
            st.session_state.session_started = False
            st.rerun()
    
    # Main question area
    st.markdown("---")
    
    # Display current question
    st.subheader("📝 Current Question:")
    st.info(st.session_state.current_question)
    
    # Change Question button with loading state
    if st.button("🔄 Generate New Question", type="secondary"):
        with st.spinner("🤖 AI is generating a new question..."):
            st.session_state.current_question = generate_question_with_hf()
            st.session_state.recorded_response = ""
        st.rerun()
    
    st.markdown("---")
    
    # Voice Recording section
    st.subheader("🎙️ Record Your Response")
    
    # Audio input widget (has built-in record/stop functionality)
    audio = st.audio_input("Record your audio response")
    
    if audio:
        # Save the recorded audio
        with open("interview_response.wav", "wb") as f:
            f.write(audio.getbuffer())
        
        # Play the recorded audio
        st.audio(audio, format="audio/wav")
        
        # Show file info
        if os.path.exists("interview_response.wav"):
            file_size = os.path.getsize("interview_response.wav")
            st.success(f"✅ Audio recorded and saved! ({file_size} bytes)")
            st.session_state.recorded_response = "Audio response recorded successfully"
    
    # Manual text input as alternative
    st.subheader("✍️ Or Type Your Response:")
    manual_response = st.text_area("Type your response here:", height=150)
    
    st.markdown("---")
    
    # Submit section
    st.subheader("📤 Submit Response")
    
    if st.button("✅ Submit Response", type="primary", use_container_width=True):
        if st.session_state.recorded_response or manual_response:
            st.success("✅ Response submitted successfully!")
            st.balloons()
            
            # Show submitted response
            st.subheader("📄 Submitted Response:")
            if manual_response:
                st.write(manual_response)
            else:
                st.write("Audio response recorded and submitted")
            
            # Option to continue with new question
            if st.button("🔄 Next AI Question"):
                with st.spinner("🤖 Generating next question..."):
                    st.session_state.current_question = generate_question_with_hf()
                    st.session_state.recorded_response = ""
                st.rerun()
        else:
            st.error("❌ Please record or type a response before submitting!")
    
    # Session info
    st.markdown("---")
    st.caption("🤖 Powered by Hugging Face AI models! Questions are dynamically generated for a unique practice experience.")