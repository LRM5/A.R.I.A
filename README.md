# A.R.I.A. - Advanced Responsive Intelligent Assistant

A sophisticated AI assistant inspired by JARVIS from Iron Man, built with Python and modern web technologies.

## 🚀 Features

- **Voice Recognition**: Wake word detection ("Aria") and voice commands
- **Text-to-Speech**: Natural voice responses
- **Web Interface**: Modern, responsive chat UI with real-time messaging
- **AI Integration**: Powered by Google Gemini 1.5 Pro
- **Multi-Modal**: Both command-line and web-based interfaces
- **Smart Home Ready**: Modular architecture for future integrations

## 📋 Prerequisites

- Python 3.8+
- macOS (tested on Apple Silicon M1/M2/M3)
- Google Gemini API key
- Microphone and speakers

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd A.R.I.A
```

### 2. Install Dependencies
```bash
python3 -m pip install --upgrade pip setuptools wheel
python3 -m pip install flask google-generativeai python-dotenv speechrecognition pyttsx3
```

### 3. Set Up Environment Variables
Create a `.env` file in the project directory:
```bash
echo 'GEMINI_API_KEY="your-actual-gemini-api-key"' > .env
```

**Get your API key from:** [Google AI Studio](https://aistudio.google.com/)

### 4. Voice Recognition Setup (Optional)

For voice recognition on macOS, you may need to install PyAudio:

```bash
# Uninstall existing packages
brew uninstall portaudio
python3 -m pip uninstall pyaudio -y

# Update and reinstall
brew update
python3 -m pip install --upgrade pip setuptools wheel
brew install portaudio --HEAD

# Install PyAudio with correct paths
python3 -m pip install pyaudio --global-option="build_ext" --global-option="-I/usr/local/include" --global-option="-L/usr/local/lib"
```

**Note:** If PyAudio installation fails, the web interface will still work with browser-based voice recognition.

## 🎯 Usage

### Web Interface (Recommended)
```bash
python3 app.py
```
Open your browser to: `http://localhost:5001`

**Features:**
- Real-time chat with A.R.I.A.
- Voice input/output (browser-based)
- Wake word detection ("Aria")
- Chat history
- Responsive design

### Command Line Interface
```bash
python3 Core.py
```

**Features:**
- Text-only mode (if voice recognition unavailable)
- Voice commands with wake word
- Direct AI interaction

## 🎤 Voice Commands

### Wake Word
- Say "**Aria**" to activate the assistant

### Example Commands
- "What's the weather today?"
- "Tell me a joke"
- "Set a timer for 5 minutes"
- "Goodbye Aria" (to exit)

## 🏗️ Architecture

```
A.R.I.A/
├── app.py                 # Flask web server
├── Core.py               # Command-line interface
├── templates/
│   └── index.html        # Web UI
├── .env                  # Environment variables
└── README.md            # This file
```

### Components

1. **Web Interface** (`app.py`)
   - Flask server with REST API
   - Real-time chat functionality
   - Session management

2. **Core Assistant** (`Core.py`)
   - Voice recognition and TTS
   - Wake word detection
   - AI integration

3. **Frontend** (`templates/index.html`)
   - Modern, responsive UI
   - Web Speech API integration
   - Real-time messaging

## 🔧 Configuration

### Environment Variables
- `GEMINI_API_KEY`: Your Google Gemini API key
- `SECRET_KEY`: Flask secret key (optional, auto-generated)

### Customization
- **Wake Word**: Change `WAKE_WORD` in `Core.py`
- **Voice Settings**: Modify TTS parameters in the web interface
- **AI Personality**: Edit the persona prompt in both files

## 🚧 Troubleshooting

### PyAudio Issues on macOS
If you encounter PyAudio installation problems:

1. **Use the web interface** - it works without PyAudio
2. **Try the installation steps above** with correct Homebrew paths
3. **Use Conda/Miniforge** for easier audio support

### API Key Issues
- Ensure your `.env` file is in the project root
- Verify your API key is valid and has sufficient quota
- Check the model name is correct (`models/gemini-1.5-pro-latest`)

### Port Issues
- If port 5000 is in use (AirPlay on macOS), the app automatically uses port 5001
- Change the port in `app.py` if needed

## 🔮 Future Features

- [ ] Smart home integration
- [ ] Camera/facial recognition
- [ ] iPhone spam blocking
- [ ] Custom voice cloning
- [ ] Multi-language support
- [ ] Plugin system

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source. Feel free to use and modify as needed.

## 🙏 Acknowledgments

- Inspired by JARVIS from Iron Man
- Built with Google Gemini AI
- Uses Web Speech API for browser-based voice features

---

**A.R.I.A. - Your Advanced Responsive Intelligent Assistant** 🤖✨
