import asyncio
import json
from google import genai
from google.genai import types
import pyaudio

client = genai.Client()

# --- pyaudio config ---
FORMAT = pyaudio.paInt16
CHANNELS = 1
SEND_SAMPLE_RATE = 16000
RECEIVE_SAMPLE_RATE = 24000
CHUNK_SIZE = 1024

pya = pyaudio.PyAudio()

# --- User Info Storage ---
current_user_info = {
    "name": None,
    "date_of_move": None,
    "street": None,
    "postal_code": None,
    "city": None,
    "previous_address": None,
}

# --- Tool Definitions ---
FUNCTION_DECLARATIONS = [
    types.FunctionDeclaration(
        name="update_user_info",
        description=(
            "Updates the current user information being collected for "
            "the Meldeschein form."
        ),
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "name": types.Schema(
                    type=types.Type.STRING,
                    description="User's full name",
                ),
                "date_of_move": types.Schema(
                    type=types.Type.STRING,
                    description="Date of move (e.g., 2025-01-15)",
                ),
                "street": types.Schema(
                    type=types.Type.STRING,
                    description="Street address",
                ),
                "postal_code": types.Schema(
                    type=types.Type.STRING,
                    description="Postal code",
                ),
                "city": types.Schema(
                    type=types.Type.STRING,
                    description="City name",
                ),
                "previous_address": types.Schema(
                    type=types.Type.STRING,
                    description="Previous address",
                ),
            },
        ),
    )
]

TOOLS = types.Tool(function_declarations=FUNCTION_DECLARATIONS)

# --- Live API config ---
MODEL = "gemini-2.5-flash-native-audio-latest"
CONFIG = {
    "response_modalities": ["AUDIO"],
    "system_instruction": (
        "You are a helpful assistant collecting Munich Meldeschein data.\n"
        "After each user interaction, call update_user_info with collected "
        "data.\nAsk for: name, date of move, street, postal code, city."
    ),
    "input_audio_transcription": {},
    "output_audio_transcription": {},
    "tools": [TOOLS],
}

audio_queue_output = asyncio.Queue()
audio_queue_mic = asyncio.Queue(maxsize=5)
audio_stream = None
is_playing = False


async def listen_audio():
    """Listens for audio and puts it into the mic audio queue."""
    print("Started listen_audio task")
    global audio_stream
    try:
        mic_info = pya.get_default_input_device_info()
        print(f"Using input device: {mic_info['name']} "
              f"(Index: {mic_info['index']})")
        audio_stream = await asyncio.to_thread(
            pya.open,
            format=FORMAT,
            channels=CHANNELS,
            rate=SEND_SAMPLE_RATE,
            input=True,
            input_device_index=int(mic_info["index"]),
            frames_per_buffer=CHUNK_SIZE,
        )
        print("Mic stream opened successfully")
    except Exception as e:
        print(f"Error opening mic: {e}")
        return

    kwargs = {"exception_on_overflow": False} if __debug__ else {}
    while True:
        try:
            data = await asyncio.to_thread(audio_stream.read, CHUNK_SIZE,
                                           **kwargs)
            await audio_queue_mic.put({"data": data, "mime_type": "audio/pcm"})
        except Exception as e:
            print(f"Error reading from mic: {e}")
            break


async def send_realtime(session):
    """Sends audio from the mic audio queue to the GenAI session."""
    print("Started send_realtime task")
    send_count = 0
    while True:
        msg = await audio_queue_mic.get()
        if not is_playing:
            await session.send_realtime_input(audio=msg)
            send_count += 1
            if send_count % 50 == 0:
                print(f"Sent {send_count} audio chunks to Gemini...")
        else:
            # Drop mic data while model is speaking to prevent echo
            pass


async def receive_audio(session):
    """Receives responses from GenAI and puts audio data into the speaker audio queue."""
    print("Started receive_audio task")
    global is_playing, current_user_info
    response_count = 0
    while True:
        try:
            print("Waiting for response from session...")
            async for response in session.receive():
                response_count += 1
                print(f"\n[Response #{response_count}]", end=" ")
                
                # Log all response fields for debugging
                if response.setup_complete:
                    print("setup_complete", end=" | ")
                if response.server_content:
                    print("server_content", end=" | ")
                if response.tool_call:
                    print("tool_call", end=" | ")
                if response.tool_call_cancellation:
                    print("tool_call_cancellation", end=" | ")
                if response.usage_metadata:
                    print("usage_metadata", end=" | ")
                if response.go_away:
                    print("go_away", end=" | ")
                if response.session_resumption_update:
                    print("session_resumption_update", end=" | ")
                if response.voice_activity_detection_signal:
                    print("vad_signal", end=" | ")
                if response.voice_activity:
                    print("voice_activity", end=" | ")
                
                # 2. HANDLE TOOL CALLS FIRST (before checking server_content)
                if response.tool_call:
                    print("  TOOL_CALL detected with function_calls")
                    tool_call = response.tool_call
                    if tool_call.function_calls:
                        print(f"    FUNCTION_CALLS: {len(tool_call.function_calls)} total")
                        function_responses = []
                        for func_call in tool_call.function_calls:
                            print(f"      Function: {func_call.name}")
                            if func_call.name == "update_user_info":
                                if func_call.args:
                                    print(f"        Args: {list(func_call.args.keys())}")
                                    # Update with provided fields
                                    for key, value in (
                                        func_call.args.items()
                                    ):
                                        if value is not None:
                                            if key in current_user_info:
                                                current_user_info[key] = (
                                                    value
                                                )
                                    print("\n[User Info Updated]:")
                                    print(json.dumps(
                                        current_user_info, indent=2))
                                # Build function response
                                function_responses.append(
                                    types.FunctionResponse(
                                        id=func_call.id,
                                        name=func_call.name,
                                        response={
                                            "output": "Successfully updated user info"
                                        }
                                    )
                                )
                        # Send tool response back to session
                        if function_responses:
                            await session.send_tool_response(
                                function_responses=function_responses
                            )
                            print("  TOOL_RESPONSE sent to model")
                
                if response.tool_call_cancellation:
                    print("  TOOL_CANCELLATION detected")
                
                if not response.server_content:
                    print()
                    continue
                
                print()

                # 1. Handle Interruption
                if response.server_content.interrupted:
                    print("\n[Model Interrupted]")
                    is_playing = False
                    while not audio_queue_output.empty():
                        audio_queue_output.get_nowait()

                # 3. Handle Model Turn (Audio, Text, Thoughts)
                if response.server_content.model_turn:
                    print(f"  MODEL_TURN with {len(response.server_content.model_turn.parts)} parts", end="")
                    for i, part in enumerate(response.server_content.model_turn.parts):
                        if part.thought:
                            print(f"\n[Gemini Thought]: {part.thought}")
                        if part.text:
                            print(f"\nGemini (Text): {part.text}")
                        if part.inline_data:
                            if isinstance(part.inline_data.data, bytes):
                                print(f"\n  AUDIO_DATA received: {len(part.inline_data.data)} bytes")
                                audio_queue_output.put_nowait(
                                    part.inline_data.data
                                )
                    print()  # newline after parts loop

                # 4. Handle User Speech Transcription
                if (transcription :=
                    response.server_content.input_transcription):
                    if transcription.text:
                        print(f"\nYou: {transcription.text}")
                # 5. Handle Model Audio Transcription
                output_transcription = (
                    response.server_content.output_transcription)
                if output_transcription:
                    if output_transcription.text:
                        print(f"\nGemini (Voice): {output_transcription.text}")
        except Exception as e:
            import traceback
            print(f"\nError in receive_audio: {e}")
            print(f"Error type: {type(e).__name__}")
            print(f"Last response_count: {response_count}")
            print("\nFull traceback:")
            traceback.print_exc()
            break


async def play_audio():
    """Plays audio from the speaker audio queue."""
    print("Started play_audio task")
    global is_playing
    try:
        stream = await asyncio.to_thread(
            pya.open,
            format=FORMAT,
            channels=CHANNELS,
            rate=RECEIVE_SAMPLE_RATE,
            output=True,
        )
        print("Speaker stream opened successfully")
    except Exception as e:
        print(f"Error opening speaker: {e}")
        return

    while True:
        bytestream = await audio_queue_output.get()
        is_playing = True
        await asyncio.to_thread(stream.write, bytestream)
        if audio_queue_output.empty():
            is_playing = False


async def run():
    """Main function to run the audio loop."""
    try:
        print(f"Connecting to Gemini (model: {MODEL})...")
        async with client.aio.live.connect(model=MODEL,
                                          config=CONFIG) as live_session:
            print("Connected to Gemini. Start speaking!")
            async with asyncio.TaskGroup() as tg:
                tg.create_task(send_realtime(live_session))
                tg.create_task(listen_audio())
                tg.create_task(receive_audio(live_session))
                tg.create_task(play_audio())
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"Error in run loop: {e}")
    finally:
        if audio_stream:
            audio_stream.close()
        pya.terminate()
        print("\nConnection closed.")


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("Interrupted by user.")
