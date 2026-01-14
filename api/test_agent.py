import os
import google.generativeai as genai
from dotenv import load_dotenv
import traceback

# Setup
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
print(f"API Key present: {bool(api_key)}")
genai.configure(api_key=api_key)

# Mock Tool
def mock_tool(name: str):
    return f"Hello {name}"

tools = [mock_tool]

try:
    print("Initializing model...")
    model_name = 'gemini-flash-latest'
    print(f"Model: {model_name}")
    model = genai.GenerativeModel(
        model_name=model_name,
        tools=tools
    )
    
    print("Starting chat...")
    chat = model.start_chat(enable_automatic_function_calling=True)
    
    print("Sending message...")
    response = chat.send_message("My name is Bruno")
    
    print("Response received.")
    print(response.text)

except Exception:
    traceback.print_exc()
