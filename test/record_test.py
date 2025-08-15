import streamlit as st

st.sidebar.title("Audio Recording App")
st.title("Record Your Audio")
st.write("Use the audio input widget below to record your audio.")

# Audio input widget (has built-in record/stop functionality)
audio = st.audio_input("Record your audio")

if audio:
    # Save the recorded audio
    with open("recorded_audio.wav", "wb") as f:
        f.write(audio.getbuffer())
        st.write("Audio recorded and saved successfully!")
    
    # Play the recorded audio
    st.audio(audio, format="audio/wav")
    
    # Show file info
    import os
    if os.path.exists("recorded_audio.wav"):
        file_size = os.path.getsize("recorded_audio.wav")
        st.info(f"File saved: recorded_audio.wav ({file_size} bytes)")
