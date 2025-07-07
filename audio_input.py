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
import io

# Ensure UTF-8 encoding for stdout
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')

# Audio method availability detection
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

# Add direct PyAudio method
audio_methods['direct_pyaudio'] = audio_methods.get('pyaudio', False)
if audio_methods['direct_pyaudio']:
    print("  Method: Direct PyAudio - Available")

# Initialize speech recognizer with better settings
recognizer = sr.Recognizer()
recognizer.pause_threshold = 0.8
recognizer.energy_threshold = 200
recognizer.dynamic_energy_threshold = True
recognizer.dynamic_energy_adjustment_damping = 0.15
recognizer.dynamic_energy_ratio = 1.5

class AudioRecoVorder:
    """Audio recording class with multiple fallback methods"""
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        self.sample_rate = 16000
        self.recording_duration = 10
        self.microphone = None
        self.recognizer = recognizer
        self.init_microphone()

    def __del__(self):
        try:
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except:
            pass

    def init_microphone(self):
        try:
            self.microphone = sr.Microphone(
                sample_rate=self.sample_rate,
                chunk_size=1024
            )
            with self.microphone as source:
                print("Calibrating microphone for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print(f"Energy threshold set to: {self.recognizer.energy_threshold}")
        except Exception as e:
            print(f"Warning: Could not initialize microphone: {e}")
            self.microphone = None

    def show_listening_screen(self, screen, ui_text, fonts):
        screen.fill((255, 255, 255))
        text = fonts['large'].render(ui_text.get('listening', 'Listening...'), True, (0, 100, 200))
        text_rect = text.get_rect(center=(screen.get_width()//2, screen.get_height()//2))
        screen.blit(text, text_rect)
        pygame.display.flip()

    def show_recording_screen(self, screen, ui_text, fonts):
        screen.fill((255, 100, 100))
        text = fonts['large'].render(ui_text.get('recording', 'Recording...'), True, (255, 255, 255))
        text_rect = text.get_rect(center=(screen.get_width()//2, screen.get_height()//2))
        screen.blit(text, text_rect)
        pygame.display.flip()

    def show_processing_screen(self, screen, ui_text, fonts):
        screen.fill((100, 100, 255))
        text = fonts['large'].render(ui_text.get('processing', 'Processing...'), True, (255, 255, 255))
        text_rect = text.get_rect(center=(screen.get_width()//2, screen.get_height()//2))
        screen.blit(text, text_rect)
        pygame.display.flip()

    def match_color(self, text, colors):
        text_lower = text.lower().strip()
        for i, color_data in enumerate(colors):
            if isinstance(color_data, (list, tuple)):
                color_name = color_data[0].lower()
                if color_name in text_lower or text_lower in color_name:
                    return i
                if len(color_data) > 2 and isinstance(color_data[2], list):
                    for alt in color_data[2]:
                        if alt.lower() in text_lower or text_lower in alt.lower():
                            return i
            else:
                if isinstance(color_data, str) and color_data.lower() in text_lower:
                    return i
        return None

    def get_input(self, colors, screen, ui_text, fonts):
        try:
            if not self.microphone:
                self.init_microphone()
                if not self.microphone:
                    return {'success': False, 'color_index': None, 'message': 'microphone_init_failed'}
            self.show_listening_screen(screen, ui_text, fonts)
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                self.show_recording_screen(screen, ui_text, fonts)
                try:
                    print(f"Listening for up to {self.recording_duration} seconds...")
                    audio = self.recognizer.listen(
                        source,
                        timeout=2,
                        phrase_time_limit=self.recording_duration
                    )
                except sr.WaitTimeoutError:
                    return {'success': False, 'color_index': None, 'message': 'timeout'}
            self.show_processing_screen(screen, ui_text, fonts)
            recognized_text = None
            recognition_methods = [
                ('google', 'en-US'),
                ('google', 'en-IN'),
                ('google', 'en-GB'),
            ]
            for method, language in recognition_methods:
                try:
                    if method == 'google':
                        recognized_text = self.recognizer.recognize_google(
                            audio,
                            language=language,
                            show_all=False
                        )
                    elif method == 'sphinx':
                        recognized_text = self.recognizer.recognize_sphinx(audio)
                    if recognized_text:
                        print(f"Recognized with {method} ({language}): '{recognized_text}'")
                        break
                except sr.UnknownValueError:
                    continue
                except sr.RequestError as e:
                    print(f"Recognition service error: {e}")
                    continue
                except Exception as e:
                    print(f"Recognition error: {e}")
                    continue
            if not recognized_text:
                return {'success': False, 'color_index': None, 'message': 'recognition_failed'}
            print(f"Final recognized text: '{recognized_text}'")
            color_index = self.match_color(recognized_text, colors)
            if color_index is not None:
                return {'success': True, 'color_index': color_index, 'message': f'recognized_{recognized_text}'}
            else:
                return {'success': False, 'color_index': None, 'message': f'no_match_{recognized_text}'}
        except KeyboardInterrupt:
            return {'success': False, 'color_index': None, 'message': 'quit'}
        except Exception as e:
            print(f"Audio input error: {e}")
            return {'success': False, 'color_index': None, 'message': f'error_{str(e)}'}

    def record_sounddevice(self):
        """Record audio using SoundDevice library"""
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
            
            # Check if recording is not just silence (more lenient threshold)
            if np.max(np.abs(recording)) < 50:  # Reduced threshold
                print("SoundDevice: Recording appears to be silence")
                return None
            
            # Save to temporary file
            temp_file = os.path.join(self.temp_dir, "temp_sounddevice.wav")
            wavfile.write(temp_file, self.sample_rate, recording)
            
            # Verify file was created and has content
            if not os.path.exists(temp_file) or os.path.getsize(temp_file) < 1000:
                print("SoundDevice: Audio file too small or doesn't exist")
                return None
            
            print(f"SoundDevice: Created audio file of {os.path.getsize(temp_file)} bytes")
            
            # Read and return audio data
            with sr.AudioFile(temp_file) as source:
                audio = recognizer.record(source)
                return audio
                
        except Exception as e:
            print(f"SoundDevice recording failed: {e}")
            return None

    def record_pyaudio(self):
        """Record audio using PyAudio library"""
        if not audio_methods.get('pyaudio'):
            return None
        
        try:
            print(f"Recording with PyAudio for {self.recording_duration} seconds...")
            
            # Create microphone instance with specific settings
            if not self.microphone:
                self.init_microphone()
            
            if not self.microphone:
                print("PyAudio: No microphone available")
                return None
            
            with self.microphone as source:
                print("PyAudio: Adjusting for ambient noise...")
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print(f"PyAudio: Energy threshold: {recognizer.energy_threshold}")
                
                print("PyAudio: Recording...")
                # Use listen with longer timeout and phrase_time_limit
                audio = recognizer.listen(
                    source, 
                    timeout=2,  # Wait 2 seconds for speech to start
                    phrase_time_limit=self.recording_duration  # Record for up to 10 seconds
                )
                return audio
                
        except sr.WaitTimeoutError:
            print("PyAudio: No speech detected within timeout")
            return None
        except Exception as e:
            print(f"PyAudio recording failed: {e}")
            return None

    def record_system(self):
        """Record audio using system commands"""
        try:
            temp_file = os.path.join(self.temp_dir, "temp_system.wav")
            
            # Remove existing file
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            print(f"Recording with system command for {self.recording_duration} seconds...")
            
            # Try different system commands based on OS
            if sys.platform.startswith('win'):
                # Windows - use SoundRecorder or PowerShell
                cmd = f'powershell -Command "Add-Type -AssemblyName System.Speech; $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; $synth.SetOutputToWaveFile(\'{temp_file}\'); $synth.Speak(\' \'); $synth.Dispose()"'
                # Alternative: Use ffmpeg if available
                cmd_ffmpeg = f'ffmpeg -f dshow -i audio="Microphone" -t {self.recording_duration} -ar {self.sample_rate} -ac 1 "{temp_file}"'
                
                try:
                    result = subprocess.run(cmd_ffmpeg, shell=True, capture_output=True, timeout=self.recording_duration+5)
                    if result.returncode == 0:
                        cmd = cmd_ffmpeg
                except:
                    # Fallback to basic recording
                    cmd = f'echo "Windows system recording not fully implemented" && timeout {self.recording_duration}'
                
            elif sys.platform.startswith('darwin'):  # macOS
                # Use sox if available, otherwise try afplay/afrecord
                cmd = f'sox -d -r {self.sample_rate} -c 1 -b 16 "{temp_file}" trim 0 {self.recording_duration}'
                if subprocess.run(['which', 'sox'], capture_output=True).returncode != 0:
                    # Fallback to ffmpeg
                    cmd = f'ffmpeg -f avfoundation -i ":0" -t {self.recording_duration} -ar {self.sample_rate} -ac 1 "{temp_file}"'
                
            else:  # Linux
                # Try multiple Linux audio recording methods
                commands_to_try = [
                    f'arecord -f S16_LE -r {self.sample_rate} -c 1 -d {self.recording_duration} "{temp_file}"',
                    f'sox -d -r {self.sample_rate} -c 1 -b 16 "{temp_file}" trim 0 {self.recording_duration}',
                    f'ffmpeg -f alsa -i default -t {self.recording_duration} -ar {self.sample_rate} -ac 1 "{temp_file}"',
                    f'parecord --format=s16le --rate={self.sample_rate} --channels=1 --record-time={self.recording_duration} "{temp_file}"'
                ]
                
                for cmd in commands_to_try:
                    try:
                        print(f"Trying: {cmd}")
                        result = subprocess.run(cmd, shell=True, capture_output=True, timeout=self.recording_duration+5)
                        if result.returncode == 0 and os.path.exists(temp_file) and os.path.getsize(temp_file) > 1000:
                            print(f"Success with: {cmd}")
                            break
                    except Exception as e:
                        print(f"Command failed: {e}")
                        continue
                else:
                    print("All Linux recording commands failed")
                    return None
            
            if not sys.platform.startswith('linux'):  # For Windows and macOS
                try:
                    print(f"Executing: {cmd}")
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

    def record_direct_pyaudio(self):
        """Record audio directly using PyAudio (alternative approach)"""
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
            
            # Find default input device
            default_device = None
            for i in range(audio_interface.get_device_count()):
                device_info = audio_interface.get_device_info_by_index(i)
                if device_info['maxInputChannels'] > 0:
                    default_device = i
                    print(f"Using audio device: {device_info['name']}")
                    break
            
            if default_device is None:
                print("No input device found")
                audio_interface.terminate()
                return None
            
            # Open stream
            stream = audio_interface.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                input_device_index=default_device,
                frames_per_buffer=CHUNK
            )
            
            print("Recording...")
            frames = []
            
            # Record for specified duration
            for i in range(0, int(RATE / CHUNK * self.recording_duration)):
                try:
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    frames.append(data)
                except Exception as e:
                    print(f"Error reading audio chunk: {e}")
                    break
            
            print("Finished recording")
            
            # Close stream
            stream.stop_stream()
            stream.close()
            audio_interface.terminate()
            
            if not frames:
                print("No audio data recorded")
                return None
            
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
            
            print(f"Direct PyAudio: Created file of {os.path.getsize(temp_file)} bytes")
            
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
            methods_to_try = ['pyaudio', 'sounddevice', 'direct_pyaudio', 'system']
        
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

# Create global audio recorder instance
audio_recorder = AudioRecoVorder()

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
        if isinstance(color_data, (list, tuple)):
            color_name = color_data[0]
        else:
            color_name = str(color_data)
        if color_name.lower() in spoken_lower or spoken_lower in color_name.lower():
            print(f"Matched '{spoken_text}' with '{color_name}'")
            return i
    return None

def record_and_recognize_audio(current_language, colors):
    global selected_method
    try:
        audio, method_used = audio_recorder.record_audio(selected_method)
        if not audio:
            print("Recording failed - no audio data")
            return None, "Recording failed - no audio captured"
        print("Audio recorded successfully, starting recognition...")
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

def get_voice_input_with_visual_feedback(screen, ui_text, current_language, colors):
    """Get voice input with visual countdown and feedback"""

    # Ensure pygame is initialized
    if not pygame.get_init():
        pygame.init()

    clock = pygame.time.Clock()

    # Phase 1: Get ready (2 seconds)
    screen.fill((255, 255, 255))
    ready_text = pygame.font.Font(None, 48).render(ui_text.get('get_ready', 'Get Ready!'), True, (255, 100, 0))
    ready_rect = ready_text.get_rect(center=(screen.get_width()//2, screen.get_height()//2))
    screen.blit(ready_text, ready_rect)

    countdown_text = pygame.font.Font(None, 32).render("Recording will start in 2 seconds...", True, (0, 0, 0))
    countdown_rect = countdown_text.get_rect(center=(screen.get_width()//2, screen.get_height()//2 + 60))
    screen.blit(countdown_text, countdown_rect)

    pygame.display.flip()

    start_time = time.time()
    while time.time() - start_time < 2.0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None, "quit"
        clock.tick(60)

    # Phase 2: Recording with countdown
    recording_start = time.time()
    result_queue = Queue()

    def recording_thread():
        color_index, message = record_and_recognize_audio(current_language, colors)
        result_queue.put((color_index, message))

    thread = threading.Thread(target=recording_thread)
    thread.daemon = True
    thread.start()

    # Show recording feedback and countdown
    while time.time() - recording_start < audio_recorder.recording_duration:
        screen.fill((255, 100, 100))

        # Show recording indicator
        recording_text = pygame.font.Font(None, 48).render(ui_text.get('recording', 'Recording...'), True, (255, 255, 255))
        recording_rect = recording_text.get_rect(center=(screen.get_width()//2, screen.get_height()//2 - 50))
        screen.blit(recording_text, recording_rect)

        # Show countdown
        remaining = audio_recorder.recording_duration - (time.time() - recording_start)
        countdown_text = pygame.font.Font(None, 32).render(f"Time remaining: {remaining:.1f}s", True, (255, 255, 255))
        countdown_rect = countdown_text.get_rect(center=(screen.get_width()//2, screen.get_height()//2 + 50))
        screen.blit(countdown_text, countdown_rect)

        # Show instruction
        instruction_text = pygame.font.Font(None, 24).render("Say the COLOR NAME of the word shown", True, (255, 255, 255))
        instruction_rect = instruction_text.get_rect(center=(screen.get_width()//2, screen.get_height()//2 + 100))
        screen.blit(instruction_text, instruction_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None, "quit"

        clock.tick(60)

    # Phase 3: Processing
    screen.fill((100, 100, 255))
    processing_text = pygame.font.Font(None, 48).render(ui_text.get('processing', 'Processing...'), True, (255, 255, 255))
    processing_rect = processing_text.get_rect(center=(screen.get_width()//2, screen.get_height()//2))
    screen.blit(processing_text, processing_rect)
    pygame.display.flip()

    # Wait for recording thread to finish and get result
    thread.join()
    if not result_queue.empty():
        color_index, message = result_queue.get()
        return color_index, message
    else:
        return None, "No result returned"

    
def recording_thread():
 color_index, message = record_and_recognize_audio(current_language, colors)
 result_queue.put((color_index, message))
 
 thread = threading.Thread(target=recording_thread)
 thread.daemon = True
 thread.start()

    # Visual countdown during recording
 while time.time() - recording_start < audio_recorder.recording_duration:
        screen.fill((255, 100, 100))
        
        # Show recording indicator
        recording_text = pygame.font.Font(None, 48).render(ui_text.get('recording', 'Recording...'), True, (255, 255, 255))
        recording_rect = recording_text.get_rect(center=(screen.get_width()//2, screen.get_height()//2 - 50))
        screen.blit(recording_text, recording_rect)
        
        # Show countdown
        remaining = audio_recorder.recording_duration - (time.time() - recording_start)
        countdown_text = pygame.font.Font(None, 32).render(f"Time remaining: {remaining:.1f}s", True, (255, 255, 255))
        countdown_rect = countdown_text.get_rect(center=(screen.get_width()//2, screen.get_height()//2 + 50))
        screen.blit(countdown_text, countdown_rect)
        
        # Show instruction
        instruction_text = pygame.font.Font(None, 24).render("Say the COLOR NAME of the word shown", True, (255, 255, 255))
        instruction_rect = instruction_text.get_rect(center=(screen.get_width()//2, screen.get_height()//2 + 100))
        screen.blit(instruction_text, instruction_rect)
        
        pygame.display.flip()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None, "quit"
        
        time.sleep(0.1)
    
    # Phase 3: Processing
 screen.fill((100, 100, 255))
 processing_text = pygame.font.Font(None, 48).render("Processing...", True, (255, 255, 255))
 processing_rect = processing_text.get_rect(center=(screen.get_width()//2, screen.get_height()//2))
 screen.blit(processing_text, processing_rect)
 pygame.display.flip()

# Wait for recording thread to finish and get result
 thread.join()
 if not result_queue.empty():
    color_index, message = result_queue.get()
    return color_index, message
 else:
    return None, "No result returned"


def select_audio_method(screen):
     global selected_method
    
     available_methods = [(k, v) for k, v in audio_methods.items() if v]
    
     if not available_methods:
        screen.fill((255, 255, 255))
        screen.blit(pygame.font.Font(None, 48).render("No audio methods available!", True, (255, 0, 0)), (200, 300))
        screen.blit(pygame.font.Font(None, 32).render("Install audio libraries and restart", True, (0, 0, 0)), (200, 350))
        pygame.display.flip()
        time.sleep(3)
        return None
    
     if len(available_methods) == 1:
        selected_method = available_methods[0][0]
        return selected_method
    
     clock = pygame.time.Clock()
    
     while True:
        screen.fill((255, 255, 255))
        screen.blit(pygame.font.Font(None, 48).render("Select Audio Method", True, (0, 0, 200)), (300, 100))
        
        method_descriptions = {
            'sounddevice': 'SoundDevice (Recommended)',
            'pyaudio': 'PyAudio (Original)',
            'direct_pyaudio': 'Direct PyAudio',
            'system': 'System Commands',
            'pydub': 'Pydub + SimpleAudio',
            'wave_os': 'Wave + OS Commands'
        }
        
        for i, (method, available) in enumerate(available_methods):
            if available:
                desc = method_descriptions.get(method, method)
                text = f"Press {i+1} for {desc}"
                screen.blit(pygame.font.Font(None, 32).render(text, True, (0, 0, 0)), (200, 200 + i*40))
        
        screen.blit(pygame.font.Font(None, 32).render("Press A for Auto-detect", True, (0, 200, 0)), (200, 200 + len(available_methods)*40))
        screen.blit(pygame.font.Font(None, 24).render("Press ESC to quit", True, (100, 100, 100)), (200, 200 + (len(available_methods)+1)*40))
        
        pygame.display.flip()
        
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

def test_microphone(screen, ui_text):
    """Test microphone functionality with GUI"""
    screen.fill((255, 255, 255))
    screen.blit(pygame.font.Font(None, 48).render("Testing Microphone...", True, (0, 0, 200)), (250, 200))
    screen.blit(pygame.font.Font(None, 32).render("You will have 3 seconds to speak!", True, (0, 0, 0)), (200, 250))
    screen.blit(pygame.font.Font(None, 24).render("Press any key to start test", True, (100, 100, 100)), (300, 300))
    pygame.display.flip()
    
    clock = pygame.time.Clock()
    
    # Wait for key press
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                waiting = False
        clock.tick(60)
    
    # Run test with dummy parameters
    colors = [("red", (255, 0, 0)), ("green", (0, 255, 0)), ("blue", (0, 0, 255))]
    color_index, message = get_voice_input_with_visual_feedback(screen, ui_text, 'english', colors)
    
    # Show results
    screen.fill((255, 255, 255))
    if color_index is not None:
        screen.blit(pygame.font.Font(None, 48).render("Test Successful!", True, (0, 200, 0)), (300, 150))
        screen.blit(pygame.font.Font(None, 32).render(f"Recognized: {message}", True, (0, 0, 0)), (200, 200))
        if color_index >= 0:
            color_name = colors[color_index][0]
            screen.blit(pygame.font.Font(None, 32).render(f"Matched color: {color_name}", True, (0, 0, 100)), (200, 250))
    else:
        screen.blit(pygame.font.Font(None, 48).render("Test Failed!", True, (255, 0, 0)), (300, 150))
        screen.blit(pygame.font.Font(None, 32).render(f"Issue: {message}", True, (0, 0, 0)), (200, 200))
    
    screen.blit(pygame.font.Font(None, 24).render("Press any key to continue", True, (100, 100, 100)), (300, 350))
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                waiting = False
        clock.tick(60)
    
    return True
def get_voice_input_with_visual_feedback(screen, ui_text, current_language, colors):
    """Get voice input with visual countdown and feedback"""
    
    # Initialize pygame if not already done
    if not pygame.get_init():
        pygame.init()
    
    clock = pygame.time.Clock()
    
    # Phase 1: Get ready (1 second)
    screen.fill((255, 255, 255))
    ready_text = pygame.font.Font(None, 48).render(ui_text['get_ready'], True, (255, 100, 0))
    ready_rect = ready_text.get_rect(center=(screen.get_width()//2, screen.get_height()//2))
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
        color_index, message = record_and_recognize_audio(current_language, colors)
        result_queue.put((color_index, message))
    
    thread = threading.Thread(target=recording_thread)
    thread.daemon = True
    thread.start()
    
    # Visual countdown during recording
    while time.time() - recording_start < audio_recorder.recording_duration:
        screen.fill((255, 255, 255))
        
        # Show recording indicator
        recording_text = pygame.font.Font(None, 48).render(ui_text['recording'], True, (255, 0, 0))
        recording_rect = recording_text.get_rect(center=(screen.get_width()//2, screen.get_height()//2 - 50))
        screen.blit(recording_text, recording_rect)
        
        # Show countdown
        remaining = audio_recorder.recording_duration - (time.time() - recording_start)
        countdown_text = pygame.font.Font(None, 32).render(f"{remaining:.1f}s", True, (0, 0, 200))
        countdown_rect = countdown_text.get_rect(center=(screen.get_width()//2, screen.get_height()//2 + 50))
        screen.blit(countdown_text, countdown_rect)
        
        pygame.display.flip()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None, "quit"
        
        time.sleep(0.1)
    
    # Phase 3: Processing
    screen.fill((255, 255, 255))
    processing_text = pygame.font.Font(None, 32).render("Processing...", True, (0, 100, 200))
    processing_rect = processing_text.get_rect(center=(screen.get_width()//2, screen.get_height()//2))
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
def get_available_methods():
    return audio_methods

def get_selected_method():
    return selected_method

def set_selected_method(method):
    global selected_method
    selected_method = method

def initialize_audio():
    global audio_recorder
    if not audio_recorder:
        audio_recorder = AudioRecoVorder()
    return True

__all__ = [
    'record_and_recognize_audio',
    'get_voice_input_with_visual_feedback',
    'select_audio_method',
    'test_microphone',
    'get_available_methods',
    'get_selected_method',
    'set_selected_method',
    'initialize_audio',
    'audio_methods',
    'selected_method'
]
