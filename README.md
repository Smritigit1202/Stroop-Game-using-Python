
# Multimodal Stroop Effect Cognitive Game

> A bilingual, accessible cognitive assessment tool with six unique input modalities. Designed for research, therapy, and adaptive neurodevelopmental testing.

---

## 🔍 Overview

This project is a Python-based **Stroop Effect Game** built with **Pygame**, supporting **six input types**:

* 🔁 Mouse Click
* ⌨️ Keyboard
* 🎧 Audio/Speech Input
* ✋ Gesture Recognition (via Webcam)
* 🔳 QR Code Scanning
* 🎨 Camera-Based Color Recognition

The game is **bilingual (English + Hindi)**, logs **response time, score, and efficiency**, and is suitable for:

* Cognitive testing
* Therapy and screening (e.g., ADHD, Autism)
* Research and education

---

## ✨ Features

| Feature             | Description                                             |
| ------------------- | ------------------------------------------------------- |
| 🎮 Game Modes       | 6 Input Types (Click, Key, Audio, Gesture, QR, Color)   |
| 🌐 Language Support | English and Hindi using Unicode-compliant fonts         |
| ⏱️ Timed Response   | Response time and efficiency tracked per question       |
| 📊 Data Logging     | Score, time, and efficiency logged in CSV + SQLite3     |
| ♻️ Modular Design   | Each input method is a separate Python module/class     |
| ⚖️ Clinical Value   | Suitable for ADHD, Dyslexia, Autism, TBI, OCD screening |
| 🎓 Educational Tool | Helps students and researchers study cognitive control  |
| ⚙️ Lightweight      | No installation-heavy dependencies, works offline       |

---

## ⚡ Input Types Explained

### 1. Mouse Click

* Color options shown as buttons
* Simple and intuitive

### 2. Keyboard Input

* Press mapped key (e.g., 'B' for Blue)
* Fast and accurate for trained users

### 3. Audio Input

* Uses `speech_recognition` with Google/STT fallback
* Microphone-based color naming

### 4. Gesture Input

* Uses `mediapipe` to detect finger gestures (1-5 fingers)
* Touchless, accessible for speech-disabled users

### 5. QR Code Input

* QR codes represent color names
* Scanned via webcam with `opencv-python`

### 6. Camera Color Input

* User shows real colored object to camera
* Detected using `numpy` + `opencv`

---

## 🔊 Language Modes

* English: Default, fast rendering
* Hindi: Unicode with Noto Sans/Mangal fonts
* Instructions and feedback shown in selected language

---
## Tabular Analysis 

| Attribute                    | Click Input                        | Key Input                                 | Audio Input                                               | Gesture Input                                       | QR Code Input                                       | Camera Color Input                                    |
|-----------------------------|------------------------------------|-------------------------------------------|-----------------------------------------------------------|----------------------------------------------------|------------------------------------------------------|--------------------------------------------------------|
| Where It Can Be Used        | Labs, clinics, schools, home       | Labs, schools, offline tests              | Speech therapy, home, ADHD testing                        | Clinics, motor control labs, interactive setups    | Visual motor control setups, clinics                | Color recognition tests, visual-cognitive screening    |
| Recommended Age Group       | 6+                                 | 6+                                        | 8+ (basic speech clarity)                                 | 8+ (gesture-capable)                               | 8+ (camera-aware)                                   | 6+                                                     |
| Effective Cognitive Domains | Attention, response inhibition     | Executive control, response speed         | Verbal processing, attention                              | Motor coordination, attention                      | Visual scanning, motor coordination                 | Color perception, visual attention                     |
| Therapeutic Use             | ADHD, executive dysfunction        | Cognitive flexibility, response time      | Speech and language delay screening                       | ADHD, motor planning issues                        | Visual-motor integration                            | Visual processing testing                              |
| Platform & Technology Used  | Pygame (Mouse)                     | Pygame (Keyboard)                         | Pygame + SpeechRecognition                                 | Pygame + MediaPipe                                 | Pygame + OpenCV + QR libraries                      | Pygame + OpenCV                                        |
| APIs / Libraries Involved   | pygame                             | pygame                                    | pygame, speech_recognition, pyaudio/sounddevice, threading | pygame, mediapipe, opencv                          | pygame, opencv, pyzbar                              | pygame, opencv, numpy                                  |
| Input Modality              | Mouse Click                        | Keyboard Press                            | Speech Recognition                                         | Finger Gesture Recognition (1–5)                  | Scanned QR corresponding to color                  | Shows a colored object in front of the camera          |
| Language Modes Supported    | English & Hindi                    | English & Hindi                           | English & Hindi (via STT)                                 | English & Hindi (instruction only)                | English & Hindi (based on QR code design)           | English & Hindi (instruction only)                     |
| Unique Selling Point (USP)  | Simple and intuitive UI            | Fastest and most accurate input mode      | Hands-free interaction, STT fallback                       | Touchless interaction, gesture mapping            | Innovative, QR-based low-cost answer method         | No external tools needed, color-based object matching    |
| Hardware Requirements       | Mouse                              | Keyboard                                  | Microphone (with PyAudio/Sounddevice)                     | Webcam                                             | Webcam                                              | Webcam                                                 |
| Internet Requirement        | No                                 | No                                        | Optional (for Google STT)                                 | No                                                 | No                                                  | No                                                      |
| Data Capturing (Score/Time) | Yes (CSV + SQLite)                 | Yes (CSV + SQLite)                        | Yes (CSV + SQLite)                                        | Yes (CSV + SQLite)                                 | Yes (CSV + SQLite)                                  | Yes (CSV + SQLite)                                     |
| Engagement Level            | High                               | Moderate                                  | High                                                      | Very High                                          | High                                                | Moderate                                                |
| Supervision Needed          | No                                 | No                                        | Yes (in younger users or noisy environments)              | Maybe (gesture mapping explanation required)       | Maybe (help in showing correct QR codes)            | Maybe (requires holding correct colors)                |
| Adaptable to Other Disorders| Yes                                | Yes                                       | Yes                                                       | Yes                                                | Yes                                                 | Yes                                                     |
| Localization / Scalability | Easy to localize                   | Easy                                      | Voice model limited to certain languages                  | Depends on gesture mapping availability            | QR code mapping can be extended                     | Can be scaled with robust color recognition           
| Limitations / Notes         | Mouse accuracy may vary on small screens | Requires understanding of key-color mapping | STT errors, background noise interference          | Lighting and finger clarity issues                | QR not scanning if lighting is poor or image is blurry | Light-dependent accuracy, background color interference |





| Input Type         | ADHD     | Autism   | OCD      | Dyslexia | TBI      | Sensory Processing Issues | Executive Dysfunction | Accessible via Motor/Speech        |
|--------------------|----------|----------|----------|----------|----------|----------------------------|------------------------|-------------------------------------|
| Click Input        | ✔️ Yes   | ✔️ Yes   | ✔️ Yes   | ✔️ Yes   | ✔️ Yes   | ❌ No                      | ✔️ Yes                | ❌ No                              |
| Key Input          | ✔️ Yes   | ✔️ Yes   | ✔️ Yes   | ✔️ Yes   | ✔️ Yes   | ❌ No                      | ✔️ Yes                | ❌ No                              |
| Audio Input        | ✔️ Yes   | ❌ No    | ❌ No    | ✔️ Yes   | ❌ No    | ❌ No                      | ✔️ Yes                | ✔️ Yes                             |
| Gesture Input      | ✔️ Yes   | ✔️ Yes   | ❌ No    | ❌ No    | ❌ No    | ❌ No                      | ✔️ Yes                | ✔️ Partial (motor only)            |
| QR Code Input      | ✔️ Yes   | ✔️ Yes   | ✔️ Yes   | ✔️ Yes   | ✔️ Yes   | ✔️ Yes                    | ✔️ Yes                | ✔️ Yes                             |
| Camera Color Input | ✔️ Yes   | ✔️ Yes   | ❌ No    | ❌ No    | ❌ No    | ❌ No                      | ✔️ Yes                | ✔️ Partial (visual-motor)          |


---
## Outputs



https://github.com/user-attachments/assets/9039eb89-99a1-43e5-bc0f-0a551f086cc8





https://github.com/user-attachments/assets/9bb557a7-7a95-4a76-95d0-47b21c537fc7



https://github.com/user-attachments/assets/847f486e-6deb-4517-9723-b73f282a8037




https://github.com/user-attachments/assets/d7f0e7ca-07ae-4abc-9394-2fcb1d4ba5d7



https://github.com/user-attachments/assets/64073bd6-f111-4be3-8425-39c5328a3555


---

## 🔗 APIs and Libraries Used

* `pygame` - UI and event handling
* `speech_recognition`, `sounddevice`, `pyaudio` - Audio input
* `opencv-python`, `numpy` - QR and color detection
* `mediapipe` - Hand gesture recognition
* `sqlite3`, `csv` - Data persistence

---

## 🌟 Efficiency Tracking

* Each session logs:

  * Score
  * Total time
  * Average response time
  * Calculated efficiency score
* Stored in `results.csv` and `stroop_data.db`

---

## 🌚 Use Cases

* Clinical: ADHD, Autism, TBI, Dyslexia screening
* Educational: Bilingual classroom training, response inhibition demos
* Research: Cognitive load, multilingual processing, STT reliability
* Therapy: Executive function development, visual-motor control

---

## 🔄 Version Info

* Fully working prototype
* 6 working modes
* Compare option between English/Hindi performance
* Stable for offline use

---

## ⚡ Future Enhancements

* 💪 Add difficulty levels (speed, distractors)
* 🤝 Multiplayer / competitive mode for classrooms
* 🔥 Add EEG/eye-tracking compatibility
* ♾ Integration with mobile camera (Android/iOS)
* 🏛 Personalized therapy profiles using DB logs

---

## 📚 Citation & References

1. Stroop, J. R. (1935). Studies of interference in serial verbal reactions. *Journal of Experimental Psychology*
2. PMC10818498 - Motion-based Stroop ADHD testing using Kinect
3. PMC8238329 - Stroop interference in Dyslexia using ERP
4. PubMed19413483 - Gesture and speech integration in Stroop tasks

---


## 🙏 Acknowledgements

Developed by **Smriti Aggarwal**

