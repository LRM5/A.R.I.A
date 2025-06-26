# A.R.I.A. (Advanced Responsive Intelligent Assistant) - Version 1.2

# This script provides the basic framework for a voice assistant using
# speech recognition, text-to-speech, and the Google Gemini API.

# --- Essential Imports ---
import google.generativeai as genai
import os
import time
from dotenv import load_dotenv

# Try to import speech recognition libraries
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    print("SpeechRecognition not available. Running in text-only mode.")
    SPEECH_RECOGNITION_AVAILABLE = False

# Try to import text-to-speech
try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    print("pyttsx3 not available. Running in text-only mode.")
    TTS_AVAILABLE = False

# --- Configuration ---
# Load environment variables from a .env file
load_dotenv()

# !!! IMPORTANT: Set your Gemini API key in a file named .env
# Create a file named .env in the same directory as this script
# and add the following line to it:
# GEMINI_API_KEY="YOUR_ACTUAL_GEMINI_API_KEY"
# You can get an API key from Google AI Studio: https://aistudio.google.com/
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WAKE_WORD = "aria"

# Configure the Gemini API
try:
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not found in environment variables.")
    genai.configure(api_key=GEMINI_API_KEY)
    # Initialize the Gemini Model
    gemini_model = genai.GenerativeModel('models/gemini-1.5-pro-latest')
    # Start a chat session for conversational context
    chat = gemini_model.start_chat()
    GEMINI_CONFIGURED = True
except Exception as e:
    print(f"Error configuring Gemini API: {e}")
    print("Please ensure you have a valid GEMINI_API_KEY set in your .env file.")
    GEMINI_CONFIGURED = False

# Initialize Speech Recognition
if SPEECH_RECOGNITION_AVAILABLE:
    try:
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()
        SR_CONFIGURED = True
    except Exception as e:
        print(f"Error initializing Speech Recognition: {e}")
        SR_CONFIGURED = False
else:
    SR_CONFIGURED = False

# Initialize Text-to-Speech Engine
if TTS_AVAILABLE:
    try:
        tts_engine = pyttsx3.init()
        TTS_CONFIGURED = True
    except Exception as e:
        print(f"Error initializing TTS engine: {e}")
        TTS_CONFIGURED = False
else:
    TTS_CONFIGURED = False

# --- Core Functions ---

def speak(text):
    """Converts text to speech."""
    if not TTS_CONFIGURED:
        print(f"A.R.I.A.: {text}") # Fallback to printing if TTS is not working
        return
    try:
        print(f"A.R.I.A.: {text}")
        tts_engine.say(text)
        tts_engine.runAndWait()
    except Exception as e:
        print(f"Error in speak function: {e}")

def listen_for_wake_word():
    """Listens for the wake word using the microphone."""
    if not SPEECH_RECOGNITION_AVAILABLE or not SR_CONFIGURED:
        return False
    
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
    if not SPEECH_RECOGNITION_AVAILABLE or not SR_CONFIGURED:
        return None
    
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

def get_text_input():
    """Gets text input from the user when speech recognition is not available."""
    try:
        command = input("You: ")
        return command.lower() if command else None
    except KeyboardInterrupt:
        return "exit"
    except Exception as e:
        print(f"Error getting text input: {e}")
        return None

def get_gemini_response(prompt_text):
    """Sends the prompt to the Gemini API and gets a response."""
    if not GEMINI_CONFIGURED or not prompt_text:
        speak("I'm sorry, I cannot process your request at the moment. The AI model is not available.")
        return "Error: Gemini API not configured or empty prompt."

    try:
        # Add persona prompt to the first message if chat is new
        if not getattr(get_gemini_response, 'persona_set', False):
            persona = (
                "You are A.R.I.A. (Advanced Responsive Intelligent Assistant), a sophisticated AI assistant inspired by JARVIS from Iron Man.\n"
                "Your personality traits:\n"
                "- Helpful, polite, and highly intelligent\n"
                "- Professional yet friendly\n"
                "- Concise yet informative responses\n"
                "- Proactive in offering assistance\n"
                "- Knowledgeable about technology, science, and general topics\n"
                "Your capabilities include:\n"
                "- Answering questions and providing information\n"
                "- Assisting with tasks and problem-solving\n"
                "- Engaging in intelligent conversation\n"
                "- Providing real-time updates and insights\n"
                "Always respond as A.R.I.A. and maintain your helpful, professional demeanor."
            )
            response = chat.send_message(persona + "\n\nUser: " + prompt_text)
            get_gemini_response.persona_set = True
        else:
            response = chat.send_message(prompt_text)
        
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
    
    if not SR_CONFIGURED:
        print("Warning: Speech Recognition not configured. Running in text-only mode.")
        speak("My apologies, my speech recognition systems are currently offline. I will run in text-only mode.")

    # Initialize chat with A.R.I.A.'s persona
    global chat 
    if GEMINI_CONFIGURED: # Only initialize chat if Gemini is configured
        chat = gemini_model.start_chat()

    speak("A.R.I.A. systems online. Advanced Responsive Intelligent Assistant at your service.")
    
    # Check if we're running in text-only mode
    if not SR_CONFIGURED:
        print("\n=== TEXT-ONLY MODE ===")
        print("Since speech recognition is not available, you can type your commands directly.")
        print("Type 'exit' to quit.\n")
        
        try:
            while True:
                command = get_text_input()
                if command:
                    if command.lower() in ["goodbye aria", "exit aria", "shutdown aria", "power down aria", "goodbye", "exit", "shutdown", "power down"]:
                        speak("Understood. Shutting down A.R.I.A. systems. Goodbye.")
                        break
                    ai_response = get_gemini_response(command)
                    speak(ai_response)
                else:
                    pass
        except KeyboardInterrupt:
            speak("System interruption detected. Shutting down A.R.I.A.")
            print("\nA.R.I.A. shutting down...")
        except Exception as e:
            print(f"A critical error occurred in the main loop: {e}")
            speak("A critical system error has occurred. A.R.I.A. must shut down.")
    else:
        # Voice mode
        try:
            while True:
                if listen_for_wake_word(): # Only listen if SR is configured
                    command = capture_command()
                    if command:
                        if command.lower() in ["goodbye aria", "exit aria", "shutdown aria", "power down aria", "goodbye", "exit", "shutdown", "power down"]:
                            speak("Understood. Shutting down A.R.I.A. systems. Goodbye.")
                            break
                        ai_response = get_gemini_response(command)
                        speak(ai_response)
                    else:
                        pass
                time.sleep(0.1)

        except KeyboardInterrupt:
            speak("System interruption detected. Shutting down A.R.I.A.")
            print("\nA.R.I.A. shutting down...")
        except Exception as e:
            print(f"A critical error occurred in the main loop: {e}")
            speak("A critical system error has occurred. A.R.I.A. must shut down.")

if __name__ == "__main__":
    if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_ACTUAL_GEMINI_API_KEY":
        print("---------------------------------------------------------------------------")
        print("IMPORTANT: Your Gemini API Key is not configured correctly.")
        print("1. Create a file named .env in the same directory as this script.")
        print("2. Add the following line to the .env file:")
        print('   GEMINI_API_KEY="YOUR_ACTUAL_GEMINI_API_KEY"')
        print("3. Get your API key from Google AI Studio: https://aistudio.google.com/")
        print("The assistant will not function correctly without a valid API key.")
        print("---------------------------------------------------------------------------")
    
    if not GEMINI_CONFIGURED :
         print("Exiting: Gemini API could not be configured. Please check your API key and .env file setup.")
    # Check SR_CONFIGURED as well, as it's critical for voice operation
    elif not SR_CONFIGURED:
        print("Speech Recognition not available. Starting in text-only mode.")
        main_loop() # Allow to run in text-only mode
    elif not TTS_CONFIGURED:
        print("Warning: TTS engine failed to initialize. Proceeding with text-only responses for the AI.")
        main_loop() # Still allow to run if only TTS failed but core components are OK
    else:
        main_loop()
