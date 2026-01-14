import os
import google.generativeai as genai
from dotenv import load_dotenv
import traceback

# Setup
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

# Mock the agent class behavior to reproduce
class MockAgent:
    def __init__(self):
        self.current_state = {}
        
        # Define tool exactly as in agent.py
        def update_ui(name: str = None, city: str = None, address: str = None, date_of_birth: str = None, progress: int = 0):
            """
            Updates the user interface.
            """
            print(f"DEBUG: Updating UI State: {name}, {city}, {progress}")
            return "UI Updated"

        self.tools = [update_ui]
        
        print(f"Initializing agent with model: gemini-2.5-flash-lite-preview-09-2025")
        self.model = genai.GenerativeModel(
            model_name='gemini-2.5-flash-lite-preview-09-2025',
            tools=self.tools,
            system_instruction="You are a helpful assistant."
        )
        self.chat = self.model.start_chat(enable_automatic_function_calling=True)

    def run(self):
        try:
            print("Sending message...")
            response = self.chat.send_message("My name is Bruno")
            print("Response received.")
            print(response.text)
            
            # Print function calls if any (though 'update_ui' logic in mock might be hidden inside library)
            # We just want to ensure no crash.
            
        except Exception:
            traceback.print_exc()

if __name__ == "__main__":
    agent = MockAgent()
    agent.run()
