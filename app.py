from flask import Flask, render_template, request, jsonify, session
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'aria-secret-key-2024')

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel('models/gemini-1.5-pro-latest')
else:
    gemini_model = None

class ARIAChat:
    def __init__(self):
        self.chat = None
        self.reset_chat()
    
    def reset_chat(self):
        """Reset the chat session with A.R.I.A.'s persona"""
        if gemini_model:
            self.chat = gemini_model.start_chat()
    
    def send_message(self, message):
        """Send a message to A.R.I.A. and get response"""
        if not self.chat:
            return "I apologize, but my AI core is currently offline. Please check your configuration."
        
        try:
            # Add persona prompt to the first message if chat is new
            if not getattr(self, 'persona_set', False):
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
                response = self.chat.send_message(persona + "\n\nUser: " + message)
                self.persona_set = True
            else:
                response = self.chat.send_message(message)
            if response.parts:
                return response.parts[0].text
            elif hasattr(response, 'text'):
                return response.text
            else:
                return "I received a response, but couldn't process it properly."
        except Exception as e:
            return f"I encountered an error: {str(e)}"

# Initialize A.R.I.A. chat instance
aria_chat = ARIAChat()

@app.route('/')
def index():
    """Main page with the A.R.I.A. interface"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """API endpoint for sending messages to A.R.I.A."""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Get response from A.R.I.A.
        response = aria_chat.send_message(message)
        
        # Store in session for chat history
        if 'chat_history' not in session:
            session['chat_history'] = []
        
        session['chat_history'].append({
            'timestamp': datetime.now().isoformat(),
            'user_message': message,
            'aria_response': response
        })
        
        # Keep only last 50 messages to prevent session bloat
        if len(session['chat_history']) > 50:
            session['chat_history'] = session['chat_history'][-50:]
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/reset', methods=['POST'])
def reset_chat():
    """Reset the chat session"""
    try:
        aria_chat.reset_chat()
        session['chat_history'] = []
        return jsonify({'message': 'Chat reset successfully'})
    except Exception as e:
        return jsonify({'error': f'Error resetting chat: {str(e)}'}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get chat history"""
    return jsonify(session.get('chat_history', []))

@app.route('/api/status', methods=['GET'])
def status():
    """Get A.R.I.A. system status"""
    return jsonify({
        'status': 'online' if gemini_model else 'offline',
        'gemini_configured': gemini_model is not None,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    if not GEMINI_API_KEY:
        print("⚠️  WARNING: GEMINI_API_KEY not found in environment variables!")
        print("   Create a .env file with: GEMINI_API_KEY='your-api-key-here'")
        print("   A.R.I.A. will run in offline mode.")
    
    print("🚀 Starting A.R.I.A. Web Interface...")
    print("   Open your browser to: http://localhost:5001")
    print("   Press Ctrl+C to stop the server")
    
    app.run(debug=True, host='0.0.0.0', port=5001) 