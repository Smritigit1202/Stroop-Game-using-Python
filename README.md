
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

## Outputs



https://github.com/user-attachments/assets/bbf08270-f194-45ab-823b-9f66a3c2ff78



https://github.com/user-attachments/assets/38c2c552-2733-4d85-9cce-b7daeffc3d68


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

