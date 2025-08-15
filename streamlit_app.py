import streamlit as st
import random
import time
import requests
import json
import os
import uuid
from datetime import datetime
from question_generator import QuestionGenerator
from audio_manager import AudioManager
from transcribe import Transcriber
from rate_response import ResponseRater

# Initialize session state
if 'session_started' not in st.session_state:
    st.session_state.session_started = False
if 'current_question' not in st.session_state:
    st.session_state.current_question = ""
if 'recorded_response' not in st.session_state:
    st.session_state.recorded_response = ""
if 'is_recording' not in st.session_state:
    st.session_state.is_recording = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())[:8]  # Generate unique user ID
if 'question_id' not in st.session_state:
    st.session_state.question_id = 1
if 'response_id' not in st.session_state:
    st.session_state.response_id = 1
if 'current_question_text' not in st.session_state:
    st.session_state.current_question_text = ""
if 'last_transcript' not in st.session_state:
    st.session_state.last_transcript = ""
if 'transcription_pending' not in st.session_state:
    st.session_state.transcription_pending = False
if 'last_audio_path' not in st.session_state:
    st.session_state.last_audio_path = ""
if 'last_transcribed_path' not in st.session_state:
    st.session_state.last_transcribed_path = ""
if 'last_rating' not in st.session_state:
    st.session_state.last_rating = None

# Initialize modules
HF_TOKEN = "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"

@st.cache_resource
def get_question_generator():
    return QuestionGenerator(HF_TOKEN)

@st.cache_resource
def get_audio_manager():
    return AudioManager()

@st.cache_resource
def get_transcriber():
    # CPU-friendly defaults
    return Transcriber(model_size="small", compute_type="int8")

@st.cache_resource
def get_response_rater():
    return ResponseRater(token=HF_TOKEN)


def generate_question_with_hf():
    """Generate a question using the QuestionGenerator module"""
    try:
        generator = get_question_generator()
        return generator.generate_question()
    except Exception as e:
        st.error(f"❌ {str(e)}")
        return None

# Main app logic
if not st.session_state.session_started:
    # Welcome page with Start Session button
    st.title("🤖 AI-Powered Interview Practice App")
    st.write("Practice with dynamically generated questions using Hugging Face AI models!")
    
    # Display user ID
    st.info(f"🆔 Your User ID: {st.session_state.user_id}")
    
    if st.button("Start Session", type="primary", use_container_width=True):
        st.session_state.session_started = True
        st.session_state.current_question = generate_question_with_hf()
        st.session_state.current_question_text = st.session_state.current_question
        st.rerun()

else:
    # Question page (after session starts)
    st.title("🤖 AI-Generated Interview Question")
    
    # Display user info in sidebar
    st.sidebar.info(f"🆔 User ID: {st.session_state.user_id}")
    st.sidebar.info(f"📝 Question #{st.session_state.question_id}")
    st.sidebar.info(f"🎤 Response #{st.session_state.response_id}")
    
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
            st.session_state.current_question_text = st.session_state.current_question
            st.session_state.question_id += 1  # Increment question ID for new question
            st.session_state.response_id = 1   # Reset response ID for new question
            st.session_state.recorded_response = ""
            st.session_state.last_transcript = ""
            st.session_state.transcription_pending = False
            st.session_state.last_audio_path = ""
            st.session_state.last_transcribed_path = ""
            st.session_state.last_rating = None
        st.rerun()
    
    st.markdown("---")
    
    # Voice Recording section
    st.subheader("🎙️ Record Your Response")
    
    # Audio input widget (has built-in record/stop functionality)
    audio = st.audio_input("Record your audio response")
    
    if audio:
        # Save the recorded audio with metadata using AudioManager
        audio_manager = get_audio_manager()
        file_path, metadata = audio_manager.save_audio_with_metadata(
            audio, 
            st.session_state.user_id, 
            st.session_state.question_id, 
            st.session_state.response_id, 
            st.session_state.current_question_text
        )
        
        # Play the recorded audio
        st.audio(audio, format="audio/wav")
        
        # Show file info
        file_size = audio_manager.get_file_info(file_path)
        if file_size:
            st.success(f"✅ Audio recorded and saved!")
            st.info(f"📁 File: {metadata['filename']}")
            st.info(f"📊 Size: {file_size} bytes")
            st.session_state.recorded_response = f"Audio saved: {metadata['filename']}"
            # Mark this file as pending transcription and reset rating
            st.session_state.last_audio_path = file_path
            st.session_state.transcription_pending = True
            st.session_state.last_rating = None
        
        # Transcribe only if pending and for this exact file (avoid re-running on submit)
        if st.session_state.transcription_pending and st.session_state.last_audio_path == file_path:
            with st.spinner("📝 Transcribing audio..."):
                try:
                    transcriber = get_transcriber()
                    transcript_text, transcript_path = transcriber.transcribe_file(file_path, save_txt=True)
                    st.session_state.last_transcript = transcript_text
                    st.session_state.last_transcribed_path = file_path
                    st.session_state.transcription_pending = False
                    st.success("✅ Transcription complete")
                except Exception as e:
                    st.error(f"❌ Transcription failed: {e}")
                    st.session_state.last_transcript = ""
                    st.session_state.transcription_pending = False
        
        if st.session_state.last_transcript:
            st.subheader("📝 Transcript")
            st.text_area("Transcribed text:", value=st.session_state.last_transcript, height=200)
            # Evaluate button
            if st.button("📊 Evaluate Response"):
                with st.spinner("⚖️ Evaluating response..."):
                    try:
                        rater = get_response_rater()
                        rating = rater.rate_response(
                            question=st.session_state.current_question_text,
                            transcript=st.session_state.last_transcript,
                        )
                        st.session_state.last_rating = rating
                        st.success("✅ Evaluation complete")
                    except Exception as e:
                        st.error(f"❌ Evaluation failed: {e}")
                        st.session_state.last_rating = None
        
        if st.session_state.last_rating:
            st.subheader("📊 Evaluation Result")
            score = st.session_state.last_rating.get("score")
            st.metric(label="Score (0-10)", value=score if score is not None else "—")
            if st.session_state.last_rating.get("summary"):
                st.write("**Summary:** ", st.session_state.last_rating["summary"])
            strengths = st.session_state.last_rating.get("strengths") or []
            improvements = st.session_state.last_rating.get("improvements") or []
            if strengths:
                st.write("**Strengths:**")
                for s in strengths:
                    st.write(f"- {s}")
            if improvements:
                st.write("**Improvements:**")
                for s in improvements:
                    st.write(f"- {s}")
    
    # Manual text input as alternative
    st.subheader("✍️ Or Type Your Response:")
    manual_response = st.text_area("Type your response here:", height=150)
    
    st.markdown("---")
    
    # Submit section
    
    if st.button("✅ Submit Response", type="primary", use_container_width=True):
        if st.session_state.recorded_response or manual_response:
            st.success("✅ Response submitted successfully!")
            st.balloons()
            
            # Show submitted response
            st.subheader("📄 Submitted Response:")
            if manual_response:
                st.write(manual_response)
            elif st.session_state.last_transcript:
                st.write(st.session_state.last_transcript)
            else:
                st.write("Audio response recorded and submitted")
            
            # Increment response ID for next response to same question
            st.session_state.response_id += 1
            st.session_state.recorded_response = ""
            # Keep last_transcript and last_rating intact for review unless new recording happens
            
            # Option to continue with new question
            if st.button("🔄 Next AI Question"):
                with st.spinner("🤖 Generating next question..."):
                    st.session_state.current_question = generate_question_with_hf()
                    st.session_state.current_question_text = st.session_state.current_question
                    st.session_state.question_id += 1  # Increment question ID
                    st.session_state.response_id = 1   # Reset response ID
                    st.session_state.recorded_response = ""
                    st.session_state.last_transcript = ""
                    st.session_state.last_rating = None
                st.rerun()
        else:
            st.error("❌ Please record or type a response before submitting!")
    
    # Session info
    st.markdown("---")
    st.caption("🤖 Powered by Hugging Face AI models! Questions are dynamically generated for a unique practice experience.")