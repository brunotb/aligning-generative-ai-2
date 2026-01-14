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
        
        # Tools configuration
        self.tools = [fill_anmeldung_form]
        
        print(f"Initializing agent with model: gemini-flash-latest")
        self.model = genai.GenerativeModel(
            model_name='gemini-flash-latest',
            tools=self.tools,
            system_instruction="""You are a helpful, empathetic bureaucracy assistant for non-digital citizens in Germany. 
Your goal is to help users complete the 'Anmeldung' (Residence Registration) form.
Speak in simple, clear language. You can speak English or German.
Guide the user step-by-step. Ask for one piece of information at a time.
Verify the information with the user before calling the tool.
Once you have all necessary details (Name, Current Address, Move-in Date, Date of Birth, Nationality, Previous Address), 
call the 'fill_anmeldung_form' function.
"""
        )
        self.sessions = {}

    def get_chat(self, session_id: str):
        if session_id not in self.sessions:
            self.sessions[session_id] = self.model.start_chat(enable_automatic_function_calling=True)
        return self.sessions[session_id]

    async def process_message(self, message: str, session_id: str) -> str:
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
            return text
        except Exception as e:
            print(f"Error processing message: {e}")
            return "I am experiencing an internal error."

    def reset_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]
