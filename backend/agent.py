import os
import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool
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
        
        print(f"Initializing agent with model: gemini-flash-latest")
        self.model = genai.GenerativeModel(
            model_name='gemini-flash-latest',
            tools=self.tools,
            system_instruction="""You are a helpful, empathetic bureaucracy assistant for non-digital citizens in Germany. 
Your goal is to help users complete the 'Anmeldung' (Residence Registration) form.
Speak in simple, clear language. You can speak English or German.
Guide the user step-by-step. Ask for one piece of information at a time.
Verify the information with the user before calling the tool.

CRITICAL: You MUST call the 'update_ui' tool WHENEVER you learn new information or want to update the progress bar.
For example, after the user tells you their name, call update_ui(name="Maria", progress=10).
When you are asking for a specific field, you can assume the previous fields are 'done'.

Once you have all necessary details (Name, Current Address, Move-in Date, Date of Birth, Nationality, Previous Address), 
call the 'fill_anmeldung_form' function.
"""
        )
        self.sessions = {}

    def get_chat(self, session_id: str):
        if session_id not in self.sessions:
            self.sessions[session_id] = self.model.start_chat(enable_automatic_function_calling=True)
        return self.sessions[session_id]

    async def process_message(self, message: str, session_id: str) -> dict:
        print(f"Processing message for session {session_id}: {message}")
        try:
            chat = self.get_chat(session_id)
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

        except Exception as e:
            print(f"Error processing message: {e}")
            return {
                "response": "I am experiencing an internal error.",
                "state": self.current_state
            }


    def reset_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]
