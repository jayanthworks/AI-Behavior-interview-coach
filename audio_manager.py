import os
import json
from datetime import datetime

class AudioManager:
    def __init__(self):
        self.recordings_dir = "recordings"
        # Create recordings directory if it doesn't exist
        if not os.path.exists(self.recordings_dir):
            os.makedirs(self.recordings_dir)
    
    def save_audio_with_metadata(self, audio_data, user_id, question_id, response_id, question_text):
        """Save audio file with unique naming based on user, question, and response IDs"""
        # Create filename with metadata
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"user_{user_id}_q{question_id}_r{response_id}_{timestamp}.wav"
        
        # Save audio file
        file_path = os.path.join(self.recordings_dir, filename)
        with open(file_path, "wb") as f:
            f.write(audio_data.getbuffer())
        
        # Save metadata
        metadata = {
            "user_id": user_id,
            "question_id": question_id,
            "response_id": response_id,
            "question_text": question_text,
            "timestamp": timestamp,
            "filename": filename,
            "file_path": file_path
        }
        
        # Save metadata to JSON file
        metadata_file = os.path.join(self.recordings_dir, f"metadata_{user_id}.json")
        
        # Load existing metadata or create new
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r') as f:
                all_metadata = json.load(f)
        else:
            all_metadata = []
        
        all_metadata.append(metadata)
        
        with open(metadata_file, 'w') as f:
            json.dump(all_metadata, f, indent=2)
        
        return file_path, metadata
    
    def get_file_info(self, file_path):
        """Get file size and other info"""
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            return file_size
        return None
    
    def list_user_recordings(self, user_id):
        """List all recordings for a specific user"""
        metadata_file = os.path.join(self.recordings_dir, f"metadata_{user_id}.json")
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r') as f:
                return json.load(f)
        return []

# Example usage
if __name__ == "__main__":
    # Test the audio manager
    audio_manager = AudioManager()
    
    # Example metadata
    user_id = "test123"
    question_id = 1
    response_id = 1
    question_text = "Tell me about yourself"
    
    print("Audio Manager initialized!")
    print(f"Recordings directory: {audio_manager.recordings_dir}")
    
    # List recordings for user
    recordings = audio_manager.list_user_recordings(user_id)
    print(f"Found {len(recordings)} recordings for user {user_id}")
