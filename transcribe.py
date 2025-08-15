import os
from typing import Tuple, Optional

from faster_whisper import WhisperModel


class Transcriber:
    def __init__(self, model_size: str = "small", compute_type: str = "int8") -> None:
        """Initialize the Faster-Whisper model.
        - model_size: one of tiny/base/small/medium/large-v3
        - compute_type: "int8", "int8_float16", "float32", etc. (int8 is CPU-friendly)
        """
        self.model = WhisperModel(model_size, compute_type=compute_type)

    def transcribe_file(self, audio_path: str, save_txt: bool = True, txt_path: Optional[str] = None) -> Tuple[str, Optional[str]]:
        """Transcribe a single audio file.
        Returns (transcript_text, transcript_path_or_None)
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        segments, _info = self.model.transcribe(audio_path, beam_size=1)
        transcript_text = " ".join(segment.text for segment in segments).strip()

        out_path = None
        if save_txt:
            if txt_path is None:
                base, _ = os.path.splitext(audio_path)
                txt_path = f"{base}.txt"
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(transcript_text)
            out_path = txt_path

        return transcript_text, out_path


if __name__ == "__main__":
    # Quick manual test (adjust the path before running)
    sample_path = "recordings/sample.wav"
    if os.path.exists(sample_path):
        t = Transcriber()
        text, saved = t.transcribe_file(sample_path)
        print("Transcript:\n", text)
        if saved:
            print("Saved:", saved)
    else:
        print("No sample file at:", sample_path)
