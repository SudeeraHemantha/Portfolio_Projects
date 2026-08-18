import logging
import sys
from src.commands import route_voice_command

logger = logging.getLogger("jarvis-assistant")
logging.basicConfig(level=logging.INFO)

class VoiceSynthesizer:
    def __init__(self):
        self.tts_engine = None
        self.init_engine()

    def init_engine(self):
        try:
            import pyttsx3
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 175) # Speed of speech
            self.tts_engine.setProperty('volume', 0.9) # Volume level
            logger.info("Initialized pyttsx3 Text-to-Speech synthesis engine.")
        except Exception as e:
            logger.warning(f"Audio TTS synthesis hardware fallback ({e}). Operating in silent/text mode.")
            self.tts_engine = None

    def speak(self, text: str):
        """Synthesizes text prompt into spoken audio."""
        logger.info(f"Jarvis Output: {text}")
        if self.tts_engine:
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                logger.error(f"TTS playback error: {e}")


class JarvisAssistant:
    def __init__(self):
        self.synthesizer = VoiceSynthesizer()
        self.wake_word = "jarvis"

    def process_prompt(self, prompt_text: str) -> dict:
        """
        Executes assistant workflow for a given text or transcribed audio prompt.
        """
        logger.info(f"Received Prompt: '{prompt_text}'")
        result = route_voice_command(prompt_text)
        
        # Synthesize spoken feedback
        if result.get("spoken_response"):
            self.synthesizer.speak(result["spoken_response"])
            
        return result

    def listen_and_process(self) -> dict:
        """
        Captures microphone audio stream using SpeechRecognition STT if available.
        """
        try:
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                logger.info("Listening for voice input...")
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                
            prompt = recognizer.recognize_google(audio)
            return self.process_prompt(prompt)
        except Exception as e:
            logger.warning(f"Live microphone capture notice ({e}). Use REST API or CLI prompt.")
            return {
                "status": "microphone_unavailable",
                "message": "Physical microphone unavailable. Submit prompts via /api/v1/voice/command REST API."
            }
