# A.R.I.A. (Advanced Responsive Intelligent Assistant) - Version 1

# --- Essential Imports ---
import speech_recognition as sr
import pyttsx3
import google.generativeai as genai
import os
import time

# --- Configuration ---
# !!! IMPORTANT: Replace "YOUR_GEMINI_API_KEY" with your actual Gemini API key !!!
# You can get an API key from Google AI Studio: https://aistudio.google.com/
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY" # Replace with your actual key
WAKE_WORD = "aria" 

# Configure the Gemini API
try:
    genai.configure(api_key=GEMINI_API_KEY)
    # Initialize the Gemini Model
    gemini_model = genai.GenerativeModel('gemini-pro')
    # Start a chat session for conversational context
    chat = gemini_model.start_chat(history=[]) # Initialize with empty history
    GEMINI_CONFIGURED = True
except Exception as e:
    print(f"Error configuring Gemini API: {e}")
    print("Please ensure you have a valid GEMINI_API_KEY set.")
    GEMINI_CONFIGURED = False

# Initialize Speech Recognition
recognizer = sr.Recognizer()
microphone = sr.Microphone()

# Initialize Text-to-Speech Engine
try:
    tts_engine = pyttsx3.init()
    # Optional: Configure voice properties (Uncomment and adjust as needed)
    # voices = tts_engine.getProperty('voices')
    # For a more A.R.I.A.-like voice, you might need to experiment with
    # available voices on your system or explore more advanced TTS options.
    # tts_engine.setProperty('voice', voices[0].id) # Example: Set to the first available voice
    # tts_engine.setProperty('rate', 180) # Speed of speech
    # tts_engine.setProperty('volume', 0.9) # Volume (0.0 to 1.0)
    TTS_CONFIGURED = True
except Exception as e:
    print(f"Error initializing TTS engine: {e}")
    print("Text-to-speech might not work.")
    TTS_CONFIGURED = False

# --- Core Functions ---

def speak(text):
    """Converts text to speech."""
    if not TTS_CONFIGURED:
        print(f"AI: {text}") # Fallback to printing if TTS is not working
        return
    try:
        print(f"A.R.I.A.: {text}") # Changed from J.A.R.V.I.S.
        tts_engine.say(text)
        tts_engine.runAndWait()
    except Exception as e:
        print(f"Error in speak function: {e}")

def listen_for_wake_word():
    """Listens for the wake word using the microphone."""
    if not GEMINI_CONFIGURED:
        print("Gemini API not configured. Wake word detection cannot start.")
        return False

    print(f"Listening for wake word: '{WAKE_WORD}'...")
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, phrase_time_limit=5)
            text = recognizer.recognize_google(audio).lower()
            print(f"Heard: {text}") # For debugging
            if WAKE_WORD in text:
                speak(f"Yes?") # Activation response for A.R.I.A.
                return True
        except sr.WaitTimeoutError:
            pass
        except sr.UnknownValueError:
            pass
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
        except Exception as e:
            print(f"An unexpected error occurred during wake word listening: {e}")
    return False

def capture_command():
    """Captures a command from the user after the wake word is detected."""
    if not GEMINI_CONFIGURED:
        return None

    print("Listening for your command...")
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, phrase_time_limit=10, timeout=10)
            command_text = recognizer.recognize_google(audio).lower()
            print(f"You said: {command_text}")
            return command_text
        except sr.WaitTimeoutError:
            speak("I didn't hear a command. Please try again.")
            return None
        except sr.UnknownValueError:
            speak("Sorry, I didn't understand that. Could you please repeat?")
            return None
        except sr.RequestError as e:
            speak("There was an issue with the speech recognition service.")
            print(f"Speech Recognition Request Error: {e}")
            return None
        except Exception as e:
            speak("An unexpected error occurred while capturing your command.")
            print(f"Error in capture_command: {e}")
            return None

def get_gemini_response(prompt_text):
    """Sends the prompt to the Gemini API and gets a response."""
    if not GEMINI_CONFIGURED or not prompt_text:
        speak("I'm sorry, I cannot process your request at the moment. The AI model is not available.")
        return "Error: Gemini API not configured or empty prompt."

    # Prepend a system message to guide A.R.I.A.'s persona
    # This is a simple way to inject personality.
    # You can make this more sophisticated by adding it to the chat history
    # or using specific system instruction capabilities if the API supports them directly.
    # For now, we'll just add it to the current prompt.
    # persona_prompt = f"You are A.R.I.A., an Advanced Responsive Intelligent Assistant. Respond helpfully and intelligently. User says: {prompt_text}"

    try:
        # Send message to the chat session to maintain context
        # The chat history itself will help maintain the flow.
        # For a stronger persona, you might initialize the chat history with a system message.
        response = chat.send_message(prompt_text) # Using the original prompt_text for the chat
        
        if response.parts:
            return response.parts[0].text
        elif hasattr(response, 'text'):
             return response.text
        else:
            speak("I received a response, but couldn't extract the text.")
            print(f"Unexpected Gemini response structure: {response}")
            return "Error: Could not parse Gemini response."

    except Exception as e:
        speak("I encountered an error trying to reach my intelligence core.")
        print(f"Error interacting with Gemini API: {e}")
        return f"Error: {e}"


# --- Main Loop ---
def main_loop():
    """The main loop that runs the voice assistant."""
    if not GEMINI_CONFIGURED:
        print("Cannot start main loop: Gemini API is not configured.")
        speak("My apologies, I am unable to start due to a configuration issue with my core systems.")
        return

    if not TTS_CONFIGURED:
        print("Warning: TTS engine not configured. Responses will be text-only.")

    # Initialize chat with A.R.I.A.'s persona
    # This message will be the first in the chat history.
    global chat # Ensure we are modifying the global chat object
    initial_system_message = {
        "role": "user", # Or "system" if the API differentiates. For Gemini, "user" for initial prompt is fine.
        "parts": [{
            "text": "You are A.R.I.A., an Advanced Responsive Intelligent Assistant. You are helpful, polite, and highly intelligent. Your responses should be concise yet informative. You are speaking to your user."
        }]
    }
    # The AI will respond to this, so we also add a model response to balance the history
    initial_model_response = {
        "role": "model",
        "parts": [{
            "text": "Understood. I am A.R.I.A., ready to assist."
        }]
    }
    chat = gemini_model.start_chat(history=[initial_system_message, initial_model_response])


    speak("A.R.I.A. systems online. Advanced Responsive Intelligent Assistant at your service.") # Changed
    try:
        while True:
            if listen_for_wake_word():
                command = capture_command()
                if command:
                    if command.lower() in ["goodbye aria", "exit aria", "shutdown aria", "power down aria", "goodbye", "exit", "shutdown", "power down"]:
                        speak("Understood. Shutting down A.R.I.A. systems. Goodbye.") # Changed
                        break
                    ai_response = get_gemini_response(command)
                    speak(ai_response)
                else:
                    pass
            time.sleep(0.1)

    except KeyboardInterrupt:
        speak("System interruption detected. Shutting down A.R.I.A.") # Changed
        print("\nA.R.I.A. shutting down...") # Changed
    except Exception as e:
        print(f"A critical error occurred in the main loop: {e}")
        speak("A critical system error has occurred. A.R.I.A. must shut down.") # Changed

if __name__ == "__main__":
    if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY":
        print("---------------------------------------------------------------------------")
        print("IMPORTANT: You are using the placeholder Gemini API Key.")
        print("Please replace 'YOUR_GEMINI_API_KEY' in the script with your actual key.")
        print("You can obtain a key from Google AI Studio: https://aistudio.google.com/")
        print("The assistant will not function correctly without a valid API key.")
        print("---------------------------------------------------------------------------")
    
    if not GEMINI_CONFIGURED:
         print("Exiting: Gemini API could not be configured. Please check your API key and setup.")
    elif not TTS_CONFIGURED:
        print("Warning: TTS engine failed to initialize. Proceeding with text-only responses for the AI.")
        main_loop()
    else:
        main_loop()
