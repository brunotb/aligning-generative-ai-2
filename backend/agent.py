import os
import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool
from google.api_core.exceptions import ResourceExhausted
from pdf_filler import fill_anmeldung_form

class BureaucracyAgent:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not set")
        
        genai.configure(api_key=api_key)
        
        # State for UI
        self.current_state = {
            "name": None,
            "city": None,
            "address": None,
            "date_of_birth": None,
            "progress": 0
        }

        def update_ui(name: str = None, city: str = None, address: str = None, date_of_birth: str = None, progress: int = 0):
            """
            Updates the user interface with the information collected so far.
            Call this tool immediately when you learn new information.
            
            Args:
                name: The user's full name.
                city: The city where they are moving/living.
                address: The street address.
                date_of_birth: The user's date of birth.
                progress: An integer 0-100 indicating how close we are to filling the form.
            """
            print(f"DEBUG: Updating UI State: {name}, {city}, {progress}")
            if name: self.current_state["name"] = name
            if city: self.current_state["city"] = city
            if address: self.current_state["address"] = address
            if date_of_birth: self.current_state["date_of_birth"] = date_of_birth
            if progress: self.current_state["progress"] = progress
            return "UI Updated"

        # Tools configuration
        self.tools = [fill_anmeldung_form, update_ui]
        
        # Store system instruction to manually prepend later
        self.system_instruction = """You are a helpful, empathetic bureaucracy assistant for non-digital citizens in Germany. 
Your goal is to help users complete the 'Anmeldung' (Residence Registration) form.
Speak in simple, clear language. You can speak English or German.
Guide the user step-by-step. Ask for one piece of information at a time.
"""

        print(f"Initializing agent with model: gemma-3-27b-it")
        
        # Gemma 3 27B does not support function calling or system instructions via this API yet.
        # We initialize it without tools and without system_instruction to prevent 400 Errors.
        self.model = genai.GenerativeModel(
            model_name='gemma-3-27b-it',
            # tools=self.tools, # DISABLED for Gemma
            # system_instruction=... # DISABLED for Gemma
        )
        self.sessions = {}

    def get_chat(self, session_id: str):
        if session_id not in self.sessions:
            # Disable automatic function calling for Gemma
            self.sessions[session_id] = self.model.start_chat(enable_automatic_function_calling=False)
        return self.sessions[session_id]

    async def process_message(self, message: str, session_id: str) -> dict:
        print(f"Processing message for session {session_id}: {message}")
        try:
            # Check if this is a new session to prepend system instruction
            is_new_session = session_id not in self.sessions
            chat = self.get_chat(session_id)
            
            # Manually prepend system instruction if it's the first message (or near start)
            # A simple heuristic: if history is empty (new chat)
            if not chat.history:
                 message = f"{self.system_instruction}\n\nUser: {message}"

            response = chat.send_message(message)
            
            # Debugging response
            print(f"Full Response Object: {response}")

            text = ""
            try:
                text = response.text
            except Exception as e:
                print(f"Could not access response.text: {e}")
                # Check for parts
                if response.parts:
                    for part in response.parts:
                        if part.function_call:
                            print(f"Function Call detected: {part.function_call}")
                            text = "[Executing tool...]"
                        if part.text:
                            text += part.text
            
            if not text:
                text = "I'm sorry, I didn't understand that. Could you repeat?"

            print(f"Final Response: {text}")
            
            # Return both text and current state
            return {
                "response": text,
                "state": self.current_state
            }

        except ResourceExhausted:
            print("Error: Quota exceeded.")
            return {
                "response": "I am currently overloaded (Rate Limit Reached). Please wait 30 seconds and try again.",
                "state": self.current_state
            }
        except Exception as e:
            print(f"Error processing message: {e}")
            return {
                "response": "I am experiencing an internal error.",
                "state": self.current_state
            }


    def reset_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]
