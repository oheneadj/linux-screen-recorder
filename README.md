# 🖥️ Screen Recorder (Linux, PyQt5 + FFmpeg)

A simple and effective screen recorder built with **PyQt5** and **FFmpeg**, designed for Linux users.  
Supports recording with multiple monitor selection, adjustable resolution, and audio toggle.  
Lightweight, minimal UI, and works natively with Ubuntu application menus.

---

## ✨ Features
- 🎥 Record your screen using FFmpeg
- 🖥️ Select monitor (multi-screen support)
- 🔊 Toggle audio recording (system mic)
- 📐 Choose recording resolution
- 📂 Save recordings anywhere
- 🖼️ Add to **Applications menu** with an icon (like a native app)

---

## 🚀 Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/screenrecorder.git
cd screenrecorder
````

### 2. Install dependencies

Make sure you have **Python 3**, **pip**, **FFmpeg**, and **PyQt5** installed:

```bash
sudo apt update
sudo apt install ffmpeg python3-pyqt5 python3-pyqt5.qtquick
```

If PyQt5 is not available via apt, install with pip inside a venv:

```bash
python3 -m venv venv
source venv/bin/activate
pip install pyqt5
```

### 3. Run the app

```bash
python3 screenrecorder.py
```

---

## 🖼️ Add to Applications Menu (Optional)

If you want to launch it from your Applications menu (like a native app):

1. Save your script in a permanent location, e.g.:

   ```
   ~/apps/screenrecorder/screenrecorder.py
   ```

2. Create a **desktop entry**:

   ```bash
   nano ~/.local/share/applications/screenrecorder.desktop
   ```

   Add this content:

   ```ini
   [Desktop Entry]
   Version=1.0
   Name=Screen Recorder
   Comment=Simple PyQt5 screen recorder
   Exec=python3 /home/YOUR_USERNAME/apps/screenrecorder/screenrecorder.py
   Icon=/home/YOUR_USERNAME/apps/screenrecorder/icon.png
   Terminal=false
   Type=Application
   Categories=AudioVideo;Video;
   ```

   Replace `YOUR_USERNAME` with your Linux username and update the paths.

3. Make it executable:

   ```bash
   chmod +x ~/.local/share/applications/screenrecorder.desktop
   ```

Now you’ll see **Screen Recorder** in your app launcher and can pin it to your dock.

---

## 🛠️ Usage

* Open the app
* Select **monitor**, **resolution**, and **audio option**
* Click **Start Recording**
* Click **Stop Recording** when done
* Your recording will be saved in the chosen location

---

## 📷 Screenshot

(Insert a screenshot of your app UI here)

---

## 🧾 License

MIT License – feel free to use and modify.

---

## 💡 Future Enhancements

* Add webcam overlay
* Add hotkey support
* Improve audio source selection

