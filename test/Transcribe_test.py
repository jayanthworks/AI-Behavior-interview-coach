

from faster_whisper import WhisperModel
model = WhisperModel("small")  # or "base"
segments, info = model.transcribe("C:/Users/jayan/Documents/recordings/user_5154deea_q1_r1_20250814_031751.wav", beam_size=1)
print(" ".join(s.text for s in segments))