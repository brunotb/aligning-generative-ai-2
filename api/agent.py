import os
import re
import json
import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool
from google.api_core.exceptions import ResourceExhausted
from pdf_filler import fill_anmeldung_form
from context_data import REGISTRATION_FORM_CONTENT, INFORMATION_REQUIREMENTS_CONTENT

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

        # Store system instruction to manually prepend later
        # We instruct the model to output JSON for UI updates since Tools are disabled for Gemma.
        self.system_instruction = f"""You are a helpful, empathetic bureaucracy assistant for non-digital citizens in Germany. 
Your goal is to help users complete the 'Anmeldung' (Residence Registration) form.
Speak in simple, clear language. You can speak English or German.
Guide the user step-by-step. Ask for one piece of information at a time.

Here is the context about the form and regulations you are helping with:

=== REGISTRATION FORM ===
{REGISTRATION_FORM_CONTENT}

=== INFORMATION REQUIREMENTS ===
{INFORMATION_REQUIREMENTS_CONTENT}
 


CRITICAL INSTRUCTION FOR UI UPDATES:
When you learn new information about the user (Name, City, Address, Date of Birth) or want to update the progress, YOU MUST OUTPUT A JSON BLOCK at the end of your response.
Format:
```json
{
  "name": "Maria",
  "city": "Berlin",
  "address": "Sonnenallee 1",
  "date_of_birth": "1990-01-01",
  "progress": 20
}
```
Only include fields you have learned or want to update.
Do not mention this JSON to the user. Just append it to the end of your message.
"""

        print(f"Initializing agent with model: gemma-3-27b-it")
        
        # Gemma 3 27B does not support function calling or system instructions via this API yet.
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

    def _extract_and_update_state(self, text: str) -> str:
        """
        Extracts JSON block from text, updates state, and returns clean text.
        """
        try:
            # Regex to find JSON block
            json_match = re.search(r"```json\s*({.*?})\s*```", text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                data = json.loads(json_str)
                
                print(f"DEBUG: Parsed JSON State Update: {data}")
                
                # Update State
                if "name" in data: self.current_state["name"] = data["name"]
                if "city" in data: self.current_state["city"] = data["city"]
                if "address" in data: self.current_state["address"] = data["address"]
                if "date_of_birth" in data: self.current_state["date_of_birth"] = data["date_of_birth"]
                if "progress" in data: self.current_state["progress"] = data["progress"]
                
                # Remove JSON from text so user doesn't see it (cleaning up)
                text = text.replace(json_match.group(0), "").strip()
                
        except Exception as e:
            print(f"Error parsing JSON state: {e}")
            
        return text

    async def process_message(self, message: str, session_id: str) -> dict:
        print(f"Processing message for session {session_id}: {message}")
        try:
            # Check if this is a new session to prepend system instruction
            is_new_session = session_id not in self.sessions
            chat = self.get_chat(session_id)
            
            # Manually prepend system instruction if it's the first message (or near start)
            if not chat.history:
                 message = f"{self.system_instruction}\n\nUser: {message}"

            response = chat.send_message(message)
            
            # Debugging response
            print(f"Full Response Object: {response}")

            text = ""
            try:
                text = response.text
                # Parse JSON pseudo-tool
                text = self._extract_and_update_state(text)
                
            except Exception as e:
                print(f"Could not access response.text: {e}")
            
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
        # Reset state on session reset
        self.current_state = {
            "name": None,
            "city": None,
            "address": None,
            "date_of_birth": None,
            "progress": 0
        }
