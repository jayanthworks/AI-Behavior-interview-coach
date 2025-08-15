import random
from huggingface_hub import InferenceClient

class QuestionGenerator:
    def __init__(self, token):
        self.token = token
        self.client = InferenceClient(token=token)
        
        # Interview topics
        self.topics = [
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
    
    def generate_question(self):
        """Generate a question using Hugging Face model"""
        try:
            # Select random topic
            selected_topic = random.choice(self.topics)
            prompt = f"Generate an interview question about {selected_topic}. Make it a clear, professional question and generate only the question."
            
            # Generate question using the model
            completion = self.client.chat.completions.create(
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
            raise Exception(f"Failed to generate AI question: {str(e)}")

# Example usage
if __name__ == "__main__":
    # Test the question generator
    TOKEN = "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"
    generator = QuestionGenerator(TOKEN)
    
    try:
        question = generator.generate_question()
        print("Generated Question:")
        print(question)
    except Exception as e:
        print(f"Error: {e}")
