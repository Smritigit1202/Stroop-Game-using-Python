# -*- coding: utf-8 -*-
"""
Stroop Effect Game - Fixed Audio Input Timing
This version fixes the audio input timing issues for proper user experience
"""

import pygame
import random
import time
import threading
from queue import Queue
import os
import sys
import subprocess
import json
import tempfile
import wave
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')

# Initialize pygame first
pygame.init()
screen = pygame.display.set_mode((900, 700))
pygame.display.set_caption("Stroop Effect Game - Fixed Audio Input")
clock = pygame.time.Clock()

# Try importing different audio libraries
audio_methods = {}
selected_method = None

print("=== Checking Available Audio Methods ===")

# Method 1: SoundDevice (Best PyAudio alternative)
try:
    import sounddevice as sd
    import numpy as np
    import scipy.io.wavfile as wavfile
    audio_methods['sounddevice'] = True
    print("  Method 1: SoundDevice - Available")
except ImportError as e:
    audio_methods['sounddevice'] = False
    print("  Method 1: SoundDevice - Not available:", str(e))

# Method 2: PyAudio (original, often problematic)
try:
    import pyaudio
    audio_methods['pyaudio'] = True
    print("  Method 2: PyAudio - Available")
except ImportError as e:
    audio_methods['pyaudio'] = False
    print("  Method 2: PyAudio - Not available:", str(e))

# Method 3: System commands (most universal)
audio_methods['system'] = True
print("  Method 3: System Commands - Available")

# Method 4: Pydub + SimpleAudio
try:
    import pydub
    from pydub import AudioSegment
    from pydub.playback import play
    import simpleaudio as sa
    audio_methods['pydub'] = True
    print("  Method 4: Pydub + SimpleAudio - Available")
except ImportError as e:
    audio_methods['pydub'] = False
    print("  Method 4: Pydub + SimpleAudio - Not available:", str(e))

# Method 5: Wave + OS commands
try:
    import wave
    audio_methods['wave_os'] = True
    print("  Method 5: Wave + OS Commands - Available")
except ImportError as e:
    audio_methods['wave_os'] = False
    print("  Method 5: Wave + OS Commands - Not available:", str(e))

# Speech recognition (REQUIRED)
try:
    import speech_recognition as sr
    print("  SpeechRecognition - Available")
except ImportError:
    print("  SpeechRecognition - REQUIRED! Install with: pip install SpeechRecognition")
    sys.exit(1)

# Languages and UI text
LANGUAGES = {
    'english': {
        'colors': [("red", (255, 0, 0)), ("green", (0, 255, 0)), ("blue", (0, 0, 255)),
                   ("yellow", (255, 255, 0)), ("pink", (255, 20, 147))],
        'ui': {
            'title': 'STROOP EFFECT GAME',
            'rules': 'Rules:',
            'rule1': '1. A word will appear in a COLOR',
            'rule2': '2. Ignore the WORD, focus on the COLOR',
            'instruction': 'Say the COLOR (not the word):',
            'correct': 'Correct! +1',
            'wrong': 'Wrong!',
            'timeout': "Time's up!",
            'final_score': 'Final Score',
            'accuracy': 'Accuracy',
            'restart': 'Press SPACE to play again or ESC to quit',
            'start_quit': 'Press SPACE to start or ESC to quit',
            'language_change': 'Press L to change language',
            'question': 'Question',
            'score': 'Score',
            'listening': 'Listening... Speak now!',
            'mic_error': 'Microphone error - trying next method',
            'audio_test': 'Press T to test microphone',
            'method_select': 'Press M to select audio method',
            'get_ready': 'Get ready...',
            'recording': 'Recording...'
        }
    },
    'hindi': {
        'colors': [
            ("लाल", (255, 0, 0), ["लाल", "laal", "lal", "red", "राल"]), 
            ("हरा", (0, 255, 0), ["हरा", "hara", "green", "हरी", "हरे"]), 
            ("नीला", (0, 0, 255), ["नीला", "neela", "nila", "blue", "नील", "नीली"]),
            ("पीला", (255, 255, 0), ["पीला", "peela", "pila", "yellow", "पील", "पीली"]), 
            ("गुलाबी", (255, 20, 147), ["गुलाबी", "gulabi", "pink", "गुलाब", "गुलाबे"])
        ],
        'ui': {
            'title': 'स्ट्रूप प्रभाव खेल',
            'rules': 'नियम:',
            'rule1': '1. एक शब्द एक रंग में दिखाई जाएगी',
            'rule2': '2. शब्द को नजरअंदाज करें, रंग पर ध्यान दें',
            'instruction': 'रंग का नाम बोलें (शब्द नहीं):',
            'correct': 'सही! +1',
            'wrong': 'गलत!',
            'timeout': 'समय समाप्त!',
            'final_score': 'अंतिम स्कोर',
            'accuracy': 'सटीकता',
            'restart': 'फिर से खेलने के लिए SPACE दबाएं या ESC दबाएं',
            'start_quit': 'शुरू करने के लिए SPACE दबाएं या बाहर निकलने के लिए ESC',
            'language_change': 'भाषा बदलने के लिए L दबाएं',
            'question': 'प्रश्न',
            'score': 'स्कोर',
            'listening': 'सुन रहे हैं... अब बोलें!',
            'mic_error': 'माइक्रोफोन त्रुटि - अगली विधि की कोशिश',
            'audio_test': 'माइक्रोफोन परीक्षण के लिए T दबाएं',
            'method_select': 'ऑडियो विधि चुनने के लिए M दबाएं',
            'get_ready': 'तैयार हो जाएं...',
            'recording': 'रिकॉर्ड हो रहा है...'
        }
    }
}

# Global state
current_language = 'english'
colors = LANGUAGES[current_language]['colors']
ui_text = LANGUAGES[current_language]['ui']
language_stats = {
    'english': {'score': 0, 'times': [], 'played': False},
    'hindi': {'score': 0, 'times': [], 'played': False}
}

# Audio setup
recognizer = sr.Recognizer()
recognizer.pause_threshold = 0.5
recognizer.energy_threshold = 300

# Font loading
def load_fonts():
    fonts = {}
    
    # Hindi fonts
    mangal_paths = [
        "Mangal.ttf", "./Mangal.ttf", "fonts/Mangal.ttf",
        "C:/Windows/Fonts/mangal.ttf", "/System/Library/Fonts/Mangal.ttf",
        "/usr/share/fonts/truetype/mangal/Mangal.ttf"
    ]
    
    mangal_font = None
    for path in mangal_paths:
        if os.path.exists(path):
            try:
                test_font = pygame.font.Font(path, 24)
                mangal_font = path
                break
            except:
                continue
    
    if mangal_font:
        try:
            fonts['hindi_large'] = pygame.font.Font(mangal_font, 48)
            fonts['hindi_medium'] = pygame.font.Font(mangal_font, 32)
            fonts['hindi_small'] = pygame.font.Font(mangal_font, 24)
        except:
            mangal_font = None
    
    if not mangal_font:
        hindi_fonts = ["Arial Unicode MS", "Noto Sans Devanagari", "Sanskrit 2003", "Arial"]
        for font_name in hindi_fonts:
            try:
                fonts['hindi_large'] = pygame.font.SysFont(font_name, 48)
                fonts['hindi_medium'] = pygame.font.SysFont(font_name, 32)
                fonts['hindi_small'] = pygame.font.SysFont(font_name, 24)
                break
            except:
                continue
        
        if 'hindi_large' not in fonts:
            fonts['hindi_large'] = pygame.font.Font(None, 48)
            fonts['hindi_medium'] = pygame.font.Font(None, 32)
            fonts['hindi_small'] = pygame.font.Font(None, 24)
    
    # English fonts
    fonts['english_large'] = pygame.font.SysFont("arial", 48)
    fonts['english_medium'] = pygame.font.SysFont("arial", 32)
    fonts['english_small'] = pygame.font.SysFont("arial", 24)
    
    return fonts

fonts = load_fonts()

def render_text(text, size, color):
    font_key = f"{current_language}_{size}"
    if font_key in fonts:
        try:
            return fonts[font_key].render(text, True, color)
        except:
            return fonts[f"english_{size}"].render(text, True, color)
    else:
        return fonts[f"english_{size}"].render(text, True, color)

def update_language(lang):
    global current_language, colors, ui_text
    current_language = lang
    colors = LANGUAGES[lang]['colors']
    ui_text = LANGUAGES[lang]['ui']

# ==================== AUDIO INPUT METHODS ====================

# ==================== IMPROVED AUDIO INPUT METHODS ====================

class AudioRecorder:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        self.sample_rate = 16000
        self.recording_duration = 5  # Fixed recording duration
        
    def __del__(self):
        try:
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except:
            pass

    # Method 1: SoundDevice (Most reliable)
    def record_sounddevice(self):
        if not audio_methods.get('sounddevice'):
            return None
        
        try:
            print(f"Recording with SoundDevice for {self.recording_duration} seconds...")
            recording = sd.rec(int(self.recording_duration * self.sample_rate), 
                             samplerate=self.sample_rate, channels=1, dtype='int16')
            sd.wait()
            
            # Check if recording has data
            if recording is None or len(recording) == 0:
                print("SoundDevice: No audio data recorded")
                return None
            
            # Check if recording is not just silence
            if np.max(np.abs(recording)) < 100:  # Very low threshold
                print("SoundDevice: Recording appears to be silence")
                return None
            
            # Save to temporary file
            temp_file = os.path.join(self.temp_dir, "temp_sounddevice.wav")
            wavfile.write(temp_file, self.sample_rate, recording)
            
            # Verify file was created and has content
            if not os.path.exists(temp_file) or os.path.getsize(temp_file) < 1000:
                print("SoundDevice: Audio file too small or doesn't exist")
                return None
            
            # Read and return audio data
            with sr.AudioFile(temp_file) as source:
                audio = recognizer.record(source)
                return audio
                
        except Exception as e:
            print(f"SoundDevice recording failed: {e}")
            return None

    # Method 2: PyAudio (Fixed with better error handling)
    def record_pyaudio(self):
        if not audio_methods.get('pyaudio'):
            return None
        
        try:
            print(f"Recording with PyAudio for {self.recording_duration} seconds...")
            
            # Create microphone instance with specific settings
            mic = sr.Microphone(sample_rate=self.sample_rate, chunk_size=1024)
            
            with mic as source:
                print("Adjusting for ambient noise...")
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print(f"Energy threshold: {recognizer.energy_threshold}")
                
                print("Recording...")
                # Use listen with timeout and phrase_time_limit
                audio = recognizer.listen(
                    source, 
                    timeout=1,  # Wait 1 second for speech to start
                    phrase_time_limit=self.recording_duration  # Record for exactly this duration
                )
                return audio
                
        except sr.WaitTimeoutError:
            print("PyAudio: No speech detected within timeout")
            return None
        except Exception as e:
            print(f"PyAudio recording failed: {e}")
            return None

    # Method 3: Improved System Commands
    def record_system(self):
        try:
            temp_file = os.path.join(self.temp_dir, "temp_system.wav")
            
            # Remove existing file
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            print(f"Recording with system command for {self.recording_duration} seconds...")
            
            # Try different system commands based on OS
            if sys.platform.startswith('win'):
                # Windows - use PowerShell with better audio recording
                cmd = f'powershell -Command "$duration = {self.recording_duration}; Add-Type -TypeDefinition \'using System; using System.Runtime.InteropServices; public class AudioRecorder {{ [DllImport(\\"winmm.dll\\")] public static extern int mciSendString(string lpstrCommand, System.Text.StringBuilder lpstrReturnString, int uReturnLength, IntPtr hWndCallback); }}\'; $sb = New-Object System.Text.StringBuilder(255); [AudioRecorder]::mciSendString(\\"open new type waveaudio alias capture\\", $sb, $sb.Capacity, 0); [AudioRecorder]::mciSendString(\\"set capture time format ms bitspersample 16 channels 1 samplespersec {self.sample_rate}\\", $sb, $sb.Capacity, 0); [AudioRecorder]::mciSendString(\\"record capture\\", $sb, $sb.Capacity, 0); Start-Sleep -Seconds $duration; [AudioRecorder]::mciSendString(\\"save capture {temp_file}\\", $sb, $sb.Capacity, 0); [AudioRecorder]::mciSendString(\\"close capture\\", $sb, $sb.Capacity, 0)"'
                
            elif sys.platform.startswith('darwin'):  # macOS
                # Use sox if available, otherwise try afplay/afrecord
                cmd = f'sox -d -r {self.sample_rate} -c 1 -b 16 {temp_file} trim 0 {self.recording_duration}'
                if subprocess.run(['which', 'sox'], capture_output=True).returncode != 0:
                    # Fallback to afplay/afrecord
                    cmd = f'rec -r {self.sample_rate} -c 1 -b 16 {temp_file} trim 0 {self.recording_duration}'
                
            else:  # Linux
                # Try multiple Linux audio recording methods
                commands_to_try = [
                    f'arecord -f S16_LE -r {self.sample_rate} -c 1 -d {self.recording_duration} {temp_file}',
                    f'sox -d -r {self.sample_rate} -c 1 -b 16 {temp_file} trim 0 {self.recording_duration}',
                    f'parecord --format=s16le --rate={self.sample_rate} --channels=1 --record-time={self.recording_duration} {temp_file}'
                ]
                
                for cmd in commands_to_try:
                    try:
                        result = subprocess.run(cmd, shell=True, capture_output=True, timeout=self.recording_duration+5)
                        if result.returncode == 0 and os.path.exists(temp_file) and os.path.getsize(temp_file) > 1000:
                            break
                    except:
                        continue
                else:
                    print("All Linux recording commands failed")
                    return None
            
            if not (sys.platform.startswith('linux')):  # For Windows and macOS
                try:
                    result = subprocess.run(cmd, shell=True, capture_output=True, timeout=self.recording_duration+5)
                    if result.returncode != 0:
                        print(f"System command failed with return code: {result.returncode}")
                        print(f"Error: {result.stderr.decode() if result.stderr else 'No error message'}")
                        return None
                except subprocess.TimeoutExpired:
                    print("System recording command timed out")
                    return None
                except Exception as e:
                    print(f"System command execution failed: {e}")
                    return None
            
            # Check if file was created and has reasonable size
            if not os.path.exists(temp_file):
                print("System recording: Output file doesn't exist")
                return None
            
            file_size = os.path.getsize(temp_file)
            if file_size < 1000:  # Less than 1KB is probably empty
                print(f"System recording: File too small ({file_size} bytes)")
                return None
            
            print(f"System recording: Created file of {file_size} bytes")
            
            # Try to read the audio file
            try:
                with sr.AudioFile(temp_file) as source:
                    audio = recognizer.record(source)
                    return audio
            except Exception as e:
                print(f"Failed to read recorded audio file: {e}")
                return None
                
        except Exception as e:
            print(f"System recording failed: {e}")
            return None

    # Method 4: Direct microphone with PyAudio (Alternative approach)
    def record_direct_pyaudio(self):
        if not audio_methods.get('pyaudio'):
            return None
        
        try:
            import pyaudio
            
            # Audio recording parameters
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = self.sample_rate
            CHUNK = 1024
            
            print(f"Recording directly with PyAudio for {self.recording_duration} seconds...")
            
            # Initialize PyAudio
            audio_interface = pyaudio.PyAudio()
            
            # Open stream
            stream = audio_interface.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK
            )
            
            print("Recording...")
            frames = []
            
            # Record for specified duration
            for i in range(0, int(RATE / CHUNK * self.recording_duration)):
                data = stream.read(CHUNK)
                frames.append(data)
            
            print("Finished recording")
            
            # Close stream
            stream.stop_stream()
            stream.close()
            audio_interface.terminate()
            
            # Save to temporary file
            temp_file = os.path.join(self.temp_dir, "temp_direct_pyaudio.wav")
            wf = wave.open(temp_file, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio_interface.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            
            # Verify file
            if not os.path.exists(temp_file) or os.path.getsize(temp_file) < 1000:
                print("Direct PyAudio: File too small or doesn't exist")
                return None
            
            # Read and return audio data
            with sr.AudioFile(temp_file) as source:
                audio = recognizer.record(source)
                return audio
                
        except Exception as e:
            print(f"Direct PyAudio recording failed: {e}")
            return None

    def record_audio(self, method=None):
        """Record audio using the specified method or try all methods"""
        if method:
            methods_to_try = [method]
        else:
            # Try methods in order of reliability
            methods_to_try = ['sounddevice', 'pyaudio', 'direct_pyaudio', 'system']
        
        for method_name in methods_to_try:
            if method_name == 'direct_pyaudio':
                # Always try direct PyAudio if PyAudio is available
                if not audio_methods.get('pyaudio'):
                    continue
            elif not audio_methods.get(method_name):
                continue
                
            try:
                print(f"\n--- Trying {method_name} ---")
                
                if method_name == 'sounddevice':
                    audio = self.record_sounddevice()
                elif method_name == 'pyaudio':
                    audio = self.record_pyaudio()
                elif method_name == 'direct_pyaudio':
                    audio = self.record_direct_pyaudio()
                elif method_name == 'system':
                    audio = self.record_system()
                else:
                    continue
                
                if audio:
                    print(f"  Successfully recorded with {method_name}")
                    return audio, method_name
                else:
                    print(f"  {method_name} returned no audio data")
                    
            except Exception as e:
                print(f"  Method {method_name} failed with exception: {e}")
                continue
        
        print("All recording methods failed!")
        return None, None

# ==================== IMPROVED SPEECH RECOGNITION ====================

def record_and_recognize_audio():
    """Record audio and recognize speech with better error handling"""
    global selected_method
    
    try:
        # Record audio for fixed duration
        audio, method_used = audio_recorder.record_audio(selected_method)
        
        if not audio:
            print("Recording failed - no audio data")
            return None, "Recording failed - no audio captured"
        
        print("Audio recorded successfully, starting recognition...")
        
        # Recognize speech with multiple attempts
        recognized_text = None
        recognition_error = None
        
        if current_language == 'hindi':
            recognition_configs = [
                ('hi-IN', 'Google Hindi'),
                ('en-IN', 'Google English-India'),  
                ('en-US', 'Google US English'),
            ]
        else:
            recognition_configs = [
                ('en-US', 'Google US English'),
                ('en-IN', 'Google English-India'),
                ('en-GB', 'Google UK English'),
            ]
        
        for lang_code, desc in recognition_configs:
            try:
                print(f"Trying {desc} recognition...")
                recognized_text = recognizer.recognize_google(
                    audio, 
                    language=lang_code,
                    show_all=False
                )
                print(f"  {desc} recognition successful: '{recognized_text}'")
                break
            except sr.UnknownValueError:
                print(f"  {desc}: Could not understand audio")
                recognition_error = "Could not understand speech"
                continue
            except sr.RequestError as e:
                print(f"  {desc}: Request failed - {e}")
                recognition_error = f"Recognition service error: {e}"
                continue
            except Exception as e:
                print(f"  {desc}: Unexpected error - {e}")
                recognition_error = f"Recognition error: {e}"
                continue
        
        if recognized_text:
            print(f"Final recognized text: '{recognized_text}'")
            
            # Match with colors
            if current_language == 'hindi':
                color_index = match_color_hindi(recognized_text, colors)
            else:
                color_index = match_color_english(recognized_text, colors)
            
            if color_index is not None:
                print(f"Matched with color index: {color_index}")
            else:
                print("No color match found")
            
            return color_index, recognized_text
        else:
            error_msg = recognition_error or "No speech recognized"
            print(f"Recognition failed: {error_msg}")
            return None, error_msg
        
    except Exception as e:
        error_msg = f"Audio processing error: {str(e)}"
        print(error_msg)
        return None, error_msg

# Update the audio_methods check to include direct PyAudio
audio_methods['direct_pyaudio'] = audio_methods.get('pyaudio', False)
if audio_methods['direct_pyaudio']:
    print("  Method: Direct PyAudio - Available")

# Re-create the audio recorder with improved methods
audio_recorder = AudioRecorder()

# ==================== SPEECH RECOGNITION ====================

def match_color_hindi(spoken_text, colors):
    spoken_lower = spoken_text.lower().strip()
    
    for i, color_data in enumerate(colors):
        if len(color_data) >= 3:
            color_name = color_data[0]
            alternatives = color_data[2]
            
            for alt in alternatives:
                if alt.lower() in spoken_lower or spoken_lower in alt.lower():
                    print(f"Matched '{spoken_text}' with '{color_name}' using alternative '{alt}'")
                    return i
    
    return None

def match_color_english(spoken_text, colors):
    spoken_lower = spoken_text.lower().strip()
    
    for i, color_data in enumerate(colors):
        color_name = color_data[0]
        if color_name.lower() in spoken_lower or spoken_lower in color_name.lower():
            print(f"Matched '{spoken_text}' with '{color_name}'")
            return i
    
    return None

def record_and_recognize_audio():
    """Record audio and recognize speech with proper timing"""
    global selected_method
    
    try:
        # Record audio for fixed duration
        audio, method_used = audio_recorder.record_audio(selected_method)
        
        if not audio:
            print("Recording failed")
            return None, "Recording failed"
        
        # Recognize speech
        recognized_text = None
        
        if current_language == 'hindi':
            recognition_configs = [
                ('hi-IN', 'Google Hindi'),
                ('en-IN', 'Google English-India'),
                ('en-US', 'Google US English'),
            ]
        else:
            recognition_configs = [
                ('en-US', 'Google US English'),
                ('en-IN', 'Google English-India'),
            ]
        
        for lang_code, desc in recognition_configs:
            try:
                recognized_text = recognizer.recognize_google(audio, language=lang_code)
                print(f"{desc} recognition: {recognized_text}")
                break
            except Exception as e:
                print(f"{desc} failed: {e}")
                continue
        
        if recognized_text:
            # Match with colors
            if current_language == 'hindi':
                color_index = match_color_hindi(recognized_text, colors)
            else:
                color_index = match_color_english(recognized_text, colors)
            
            return color_index, recognized_text
        else:
            return None, "No speech recognized"
        
    except Exception as e:
        print(f"Audio processing error: {e}")
        return None, f"Error: {str(e)}"

def get_voice_input_with_visual_feedback():
    """Get voice input with visual countdown and feedback"""
    
    # Phase 1: Get ready (1 second)
    screen.fill((255, 255, 255))
    ready_text = render_text(ui_text['get_ready'], 'large', (255, 100, 0))
    ready_rect = ready_text.get_rect(center=(450, 350))
    screen.blit(ready_text, ready_rect)
    pygame.display.flip()
    
    # Handle events during get ready
    start_time = time.time()
    while time.time() - start_time < 1.0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None, "quit"
        time.sleep(0.1)
    
    # Phase 2: Recording with countdown
    recording_start = time.time()
    
    # Start recording in background thread
    result_queue = Queue()
    
    def recording_thread():
        color_index, message = record_and_recognize_audio()
        result_queue.put((color_index, message))
    
    thread = threading.Thread(target=recording_thread)
    thread.daemon = True
    thread.start()
    
    # Visual countdown during recording
    while time.time() - recording_start < audio_recorder.recording_duration:
        screen.fill((255, 255, 255))
        
        # Show recording indicator
        recording_text = render_text(ui_text['recording'], 'large', (255, 0, 0))
        recording_rect = recording_text.get_rect(center=(450, 300))
        screen.blit(recording_text, recording_rect)
        
        # Show countdown
        remaining = audio_recorder.recording_duration - (time.time() - recording_start)
        countdown_text = render_text(f"{remaining:.1f}s", 'medium', (0, 0, 200))
        countdown_rect = countdown_text.get_rect(center=(450, 400))
        screen.blit(countdown_text, countdown_rect)
        
        pygame.display.flip()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None, "quit"
        
        time.sleep(0.1)
    
    # Phase 3: Processing
    screen.fill((255, 255, 255))
    processing_text = render_text("Processing...", 'medium', (0, 100, 200))
    processing_rect = processing_text.get_rect(center=(450, 350))
    screen.blit(processing_text, processing_rect)
    pygame.display.flip()
    
    # Wait for result (with timeout)
    wait_start = time.time()
    while time.time() - wait_start < 5.0:  # 5 second timeout for processing
        if not result_queue.empty():
            return result_queue.get()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None, "quit"
        
        time.sleep(0.1)
    
    return None, "Processing timeout"

# ==================== AUDIO METHOD SELECTION ====================

def select_audio_method():
    global selected_method
    
    available_methods = [(k, v) for k, v in audio_methods.items() if v]
    
    if not available_methods:
        screen.fill((255, 255, 255))
        screen.blit(render_text("No audio methods available!", 'large', (255, 0, 0)), (200, 300))
        screen.blit(render_text("Install audio libraries and restart", 'medium', (0, 0, 0)), (200, 350))
        pygame.display.flip()
        time.sleep(3)
        return None
    
    if len(available_methods) == 1:
        selected_method = available_methods[0][0]
        return selected_method
    
    screen.fill((255, 255, 255))
    screen.blit(render_text("Select Audio Method", 'large', (0, 0, 200)), (300, 100))
    
    method_descriptions = {
        'sounddevice': 'SoundDevice (Recommended)',
        'pyaudio': 'PyAudio (Original)',
        'system': 'System Commands',
        'pydub': 'Pydub + SimpleAudio',
        'wave_os': 'Wave + OS Commands'
    }
    
    for i, (method, available) in enumerate(available_methods):
        if available:
            desc = method_descriptions.get(method, method)
            text = f"Press {i+1} for {desc}"
            screen.blit(render_text(text, 'medium', (0, 0, 0)), (200, 200 + i*40))
    
    screen.blit(render_text("Press A for Auto-detect", 'medium', (0, 200, 0)), (200, 200 + len(available_methods)*40))
    screen.blit(render_text("Press ESC to quit", 'small', (100, 100, 100)), (200, 200 + (len(available_methods)+1)*40))
    
    pygame.display.flip()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                elif event.key == pygame.K_a:
                    selected_method = None  # Auto-detect
                    return 'auto'
                else:
                    # Check number keys
                    key_num = event.key - pygame.K_1
                    if 0 <= key_num < len(available_methods):
                        selected_method = available_methods[key_num][0]
                        return selected_method
        clock.tick(60)

# ==================== TESTING ====================

def test_microphone():
    screen.fill((255, 255, 255))
    screen.blit(render_text("Testing Microphone...", 'large', (0, 0, 200)), (250, 200))
    screen.blit(render_text("You will have 3 seconds to speak!", 'medium', (0, 0, 0)), (200, 250))
    screen.blit(render_text("Press any key to start test", 'small', (100, 100, 100)), (300, 300))
    pygame.display.flip()
    
    # Wait for key press
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                waiting = False
    
    # Run test
    color_index, message = get_voice_input_with_visual_feedback()
    
    # Show results
    screen.fill((255, 255, 255))
    if color_index is not None:
        screen.blit(render_text("Test Successful!", 'large', (0, 200, 0)), (300, 150))
        screen.blit(render_text(f"Recognized: {message}", 'medium', (0, 0, 0)), (200, 200))
        if color_index >= 0:
            color_name = colors[color_index][0]
            screen.blit(render_text(f"Matched color: {color_name}", 'medium', (0, 0, 100)), (200, 250))
    else:
        screen.blit(render_text("Test Failed!", 'large', (255, 0, 0)), (300, 150))
        screen.blit(render_text(f"Issue: {message}", 'medium', (0, 0, 0)), (200, 200))
    
    screen.blit(render_text("Press any key to continue", 'small', (100, 100, 100)), (300, 350))
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                waiting = False
    
    return True

# ==================== GAME LOGIC ====================

def get_color_name_and_rgb(color_data):
    if current_language == 'hindi' and len(color_data) >= 3:
        return color_data[0], color_data[1]
    else:
        return color_data[0], color_data[1]

def compare_language_stats():
    screen.fill((255, 255, 255))
    title = render_text("Comparison of Languages", 'large', (0, 0, 0))
    screen.blit(title, title.get_rect(center=(450, 60)))

    for idx, lang in enumerate(['english', 'hindi']):
        y_offset = 150 + idx * 200
        lang_stats = language_stats[lang]
        
        # Language name
        lang_name = "English" if lang == 'english' else "Hindi (हिंदी)"
        lang_text = render_text(lang_name, 'medium', (0, 0, 200))
        screen.blit(lang_text, (100, y_offset))
        
        if lang_stats['played']:
            # Score
            score_text = render_text(f"Score: {lang_stats['score']}/5", 'small', (0, 0, 0))
            screen.blit(score_text, (100, y_offset + 40))
            
            # Accuracy
            accuracy = (lang_stats['score'] / 5) * 100
            accuracy_text = render_text(f"Accuracy: {accuracy:.1f}%", 'small', (0, 0, 0))
            screen.blit(accuracy_text, (100, y_offset + 70))
            
            # Average response time
            if lang_stats['times']:
                avg_time = sum(lang_stats['times']) / len(lang_stats['times'])
                time_text = render_text(f"Avg Time: {avg_time:.2f}s", 'small', (0, 0, 0))
                screen.blit(time_text, (100, y_offset + 100))
            
            # Performance indicator
            if lang_stats['score'] >= 4:
                perf_text = render_text("Excellent!", 'small', (0, 150, 0))
            elif lang_stats['score'] >= 3:
                perf_text = render_text("Good", 'small', (0, 100, 0))
            elif lang_stats['score'] >= 2:
                perf_text = render_text("Fair", 'small', (200, 100, 0))
            else:
                perf_text = render_text("Needs Practice", 'small', (200, 0, 0))
            
            screen.blit(perf_text, (100, y_offset + 130))
        else:
            not_played_text = render_text("Not played yet", 'small', (100, 100, 100))
            screen.blit(not_played_text, (100, y_offset + 40))
    
    # Instructions
    instruction_text = render_text("Press SPACE to continue or ESC to quit", 'small', (0, 0, 0))
    screen.blit(instruction_text, (250, 600))
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False
                elif event.key == pygame.K_ESCAPE:
                    return False
        clock.tick(60)
    
    return True

def play_game():
    question_count = 0
    total_questions = 5
    score = 0
    response_times = []
    
    while question_count < total_questions:
        # Clear screen and show question info
        screen.fill((255, 255, 255))
        
        # Show question number and score
        question_text = render_text(f"{ui_text['question']} {question_count + 1}/5", 'medium', (0, 0, 0))
        score_text = render_text(f"{ui_text['score']}: {score}", 'medium', (0, 0, 0))
        # Continuation of the play_game() function and remaining code

        screen.blit(question_text, (50, 50))
        screen.blit(score_text, (650, 50))
        
        # Choose random word and color
        word_index = random.randint(0, len(colors) - 1)
        color_index = random.randint(0, len(colors) - 1)
        
        word_name, _ = get_color_name_and_rgb(colors[word_index])
        _, correct_color_rgb = get_color_name_and_rgb(colors[color_index])
        
        # Display the word in the color
        word_surface = render_text(word_name, 'large', correct_color_rgb)
        word_rect = word_surface.get_rect(center=(450, 200))
        screen.blit(word_surface, word_rect)
        
        # Show instruction
        instruction_surface = render_text(ui_text['instruction'], 'medium', (0, 0, 0))
        instruction_rect = instruction_surface.get_rect(center=(450, 300))
        screen.blit(instruction_surface, instruction_rect)
        
        # Show all possible color names for reference
        color_names = []
        for i, color_data in enumerate(colors):
            color_name, color_rgb = get_color_name_and_rgb(color_data)
            color_names.append(color_name)
        
        reference_text = " | ".join(color_names)
        ref_surface = render_text(reference_text, 'small', (100, 100, 100))
        ref_rect = ref_surface.get_rect(center=(450, 500))
        screen.blit(ref_surface, ref_rect)
        
        pygame.display.flip()
        
        # Wait a moment before starting recording
        time.sleep(1.0)
        
        # Record start time
        start_time = time.time()
        
        # Get voice input with improved timing
        user_color_index, message = get_voice_input_with_visual_feedback()
        
        # Calculate response time
        response_time = time.time() - start_time
        response_times.append(response_time)
        
        # Handle quit
        if message == "quit":
            return False
        
        # Check if quit event occurred
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        
        # Determine if answer is correct
        is_correct = user_color_index == color_index
        
        # Show result
        screen.fill((255, 255, 255))
        
        # Show the word and color again
        screen.blit(word_surface, word_rect)
        
        if is_correct:
            score += 1
            result_text = render_text(ui_text['correct'], 'large', (0, 255, 0))
        else:
            if user_color_index is not None and user_color_index >= 0:
                user_answer = colors[user_color_index][0]
                correct_answer = colors[color_index][0]
                result_text = render_text(ui_text['wrong'], 'large', (255, 0, 0))
                
                # Show what was said vs correct answer
                said_text = render_text(f"You said: {user_answer}", 'medium', (0, 0, 0))
                correct_text = render_text(f"Correct: {correct_answer}", 'medium', (0, 0, 0))
                screen.blit(said_text, (300, 400))
                screen.blit(correct_text, (300, 440))
            else:
                result_text = render_text(f"{ui_text['timeout']} - {message}", 'large', (255, 100, 0))
        
        result_rect = result_text.get_rect(center=(450, 350))
        screen.blit(result_text, result_rect)
        
        # Show response time
        time_text = render_text(f"Time: {response_time:.2f}s", 'small', (0, 0, 100))
        screen.blit(time_text, (400, 480))
        
        pygame.display.flip()
        time.sleep(2)
        
        question_count += 1
    
    # Store stats for current language
    language_stats[current_language]['score'] = score
    language_stats[current_language]['times'] = response_times
    language_stats[current_language]['played'] = True
    
    # Show final results
    screen.fill((255, 255, 255))
    
    final_score_text = render_text(f"{ui_text['final_score']}: {score}/5", 'large', (0, 0, 0))
    final_score_rect = final_score_text.get_rect(center=(450, 200))
    screen.blit(final_score_text, final_score_rect)
    
    accuracy = (score / 5) * 100
    accuracy_text = render_text(f"{ui_text['accuracy']}: {accuracy:.1f}%", 'medium', (0, 0, 0))
    accuracy_rect = accuracy_text.get_rect(center=(450, 250))
    screen.blit(accuracy_text, accuracy_rect)
    
    if response_times:
        avg_time = sum(response_times) / len(response_times)
        avg_time_text = render_text(f"Average Time: {avg_time:.2f}s", 'medium', (0, 0, 0))
        avg_time_rect = avg_time_text.get_rect(center=(450, 300))
        screen.blit(avg_time_text, avg_time_rect)
    
    restart_text = render_text(ui_text['restart'], 'small', (0, 0, 0))
    restart_rect = restart_text.get_rect(center=(450, 400))
    screen.blit(restart_text, restart_rect)
    
    lang_change_text = render_text(ui_text['language_change'], 'small', (0, 0, 0))
    lang_change_rect = lang_change_text.get_rect(center=(450, 430))
    screen.blit(lang_change_text, lang_change_rect)
    
    # Show comparison option if both languages played
    if language_stats['english']['played'] and language_stats['hindi']['played']:
        compare_text = render_text("Press C to compare languages", 'small', (0, 100, 0))
        compare_rect = compare_text.get_rect(center=(450, 460))
        screen.blit(compare_text, compare_rect)
    
    pygame.display.flip()
    
    # Wait for user input
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return True
                elif event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_l:
                    # Toggle language
                    new_lang = 'hindi' if current_language == 'english' else 'english'
                    update_language(new_lang)
                    return True
                elif event.key == pygame.K_c:
                    if language_stats['english']['played'] and language_stats['hindi']['played']:
                        if not compare_language_stats():
                            return False
                        return True
        clock.tick(60)
    
    return True

def show_menu():
    """Show main menu with options"""
    while True:
        screen.fill((255, 255, 255))
        
        # Title
        title_text = render_text(ui_text['title'], 'large', (0, 0, 200))
        title_rect = title_text.get_rect(center=(450, 100))
        screen.blit(title_text, title_rect)
        
        # Current language indicator
        lang_indicator = f"Language: {'English' if current_language == 'english' else 'Hindi (हिंदी)'}"
        lang_text = render_text(lang_indicator, 'medium', (0, 100, 0))
        lang_rect = lang_text.get_rect(center=(450, 150))
        screen.blit(lang_text, lang_rect)
        
        # Rules
        rules_text = render_text(ui_text['rules'], 'medium', (0, 0, 0))
        screen.blit(rules_text, (100, 200))
        
        rule1_text = render_text(ui_text['rule1'], 'small', (0, 0, 0))
        screen.blit(rule1_text, (120, 240))
        
        rule2_text = render_text(ui_text['rule2'], 'small', (0, 0, 0))
        screen.blit(rule2_text, (120, 270))
        
        # Instructions
        start_text = render_text(ui_text['start_quit'], 'medium', (0, 0, 0))
        start_rect = start_text.get_rect(center=(450, 350))
        screen.blit(start_text, start_rect)
        
        lang_change_text = render_text(ui_text['language_change'], 'small', (100, 100, 100))
        lang_change_rect = lang_change_text.get_rect(center=(450, 400))
        screen.blit(lang_change_text, lang_change_rect)
        
        test_text = render_text(ui_text['audio_test'], 'small', (100, 100, 100))
        test_rect = test_text.get_rect(center=(450, 430))
        screen.blit(test_text, test_rect)
        
        method_text = render_text(ui_text['method_select'], 'small', (100, 100, 100))
        method_rect = method_text.get_rect(center=(450, 460))
        screen.blit(method_text, method_rect)
        
        # Show current audio method
        if selected_method:
            method_info = f"Audio Method: {selected_method}"
        else:
            method_info = "Audio Method: Auto-detect"
        method_info_text = render_text(method_info, 'small', (0, 0, 100))
        method_info_rect = method_info_text.get_rect(center=(450, 490))
        screen.blit(method_info_text, method_info_rect)
        
        # Show comparison option if both languages played
        if language_stats['english']['played'] and language_stats['hindi']['played']:
            compare_text = render_text("Press C to compare languages", 'small', (0, 150, 0))
            compare_rect = compare_text.get_rect(center=(450, 520))
            screen.blit(compare_text, compare_rect)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return True
                elif event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_l:
                    new_lang = 'hindi' if current_language == 'english' else 'english'
                    update_language(new_lang)
                elif event.key == pygame.K_t:
                    if not test_microphone():
                        return False
                elif event.key == pygame.K_m:
                    result = select_audio_method()
                    if result is None:
                        return False
                elif event.key == pygame.K_c:
                    if language_stats['english']['played'] and language_stats['hindi']['played']:
                        if not compare_language_stats():
                            return False
        
        clock.tick(60)

def main():
    """Main game loop"""
    global selected_method
    
    print("=== Stroop Effect Game - Fixed Audio Input ===")
    
    # Select audio method if not already selected
    if selected_method is None:
        result = select_audio_method()
        if result is None:
            print("No audio method selected. Exiting.")
            pygame.quit()
            return
    
    print(f"Using audio method: {selected_method if selected_method else 'Auto-detect'}")
    
    # Main game loop
    running = True
    while running:
        # Show menu
        if show_menu():
            # Play game
            if not play_game():
                running = False
        else:
            running = False
    
    pygame.quit()
    print("Thanks for playing!")

if __name__ == "__main__":
    main()