import sys
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QSlider,
    QPushButton, QComboBox, QWidget, QCheckBox, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt, QSettings
from datetime import datetime
import threading
import os
import re

class ScreenRecorderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Screen Recorder")
        self.setGeometry(100, 100, 600, 400)

        # Main Layout
        self.central_widget = QWidget()
        self.layout = QVBoxLayout(self.central_widget)

        # Settings
        self.settings = QSettings("ScreenRecorderApp", "ScreenRecorderApp")

        # Create UI elements
        self.create_ui()

        # Set central widget
        self.setCentralWidget(self.central_widget)

        # FFmpeg process
        self.ffmpeg_process = None
        self.save_location = ""

        # Populate monitors
        self.populate_monitors()

        # Load settings
        self.load_settings()

    def get_available_monitors(self):
        """Get list of available monitors using xrandr"""
        monitors = []
        try:
            result = subprocess.run(['xrandr', '--listmonitors'], 
                                  capture_output=True, text=True, check=True)
            lines = result.stdout.strip().split('\n')
            for line in lines[1:]:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        monitor_name = parts[1].lstrip('+*')
                        if len(parts) >= 3:
                            resolution_info = parts[2]
                            match = re.match(r'(\d+)/\d+x(\d+)/\d+\+(\d+)\+(\d+)', resolution_info)
                            if match:
                                width, height, x_offset, y_offset = match.groups()
                                display_name = f"{monitor_name} ({width}x{height}) at +{x_offset},{y_offset}"
                                display_value = f":0.0+{x_offset},{y_offset}"
                                monitors.append((display_name, display_value))
        except (subprocess.CalledProcessError, FileNotFoundError):
            try:
                result = subprocess.run(['xdpyinfo', '-ext', 'XINERAMA'], 
                                      capture_output=True, text=True, check=True)
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'head #' in line:
                        match = re.search(r'head #(\d+): (\d+x\d+) @ (\d+),(\d+)', line)
                        if match:
                            head_num, resolution, x_offset, y_offset = match.groups()
                            display_name = f"Screen {head_num} ({resolution}) at +{x_offset},{y_offset}"
                            display_value = f":0.0+{x_offset},{y_offset}"
                            monitors.append((display_name, display_value))
                if not monitors:
                    monitors.append(("Primary Display (Full Screen)", ":0.0"))
            except (subprocess.CalledProcessError, FileNotFoundError):
                monitors.append(("Primary Display (Full Screen)", ":0.0"))
        if not monitors:
            monitors.append(("Primary Display (Full Screen)", ":0.0"))
        return monitors

    def populate_monitors(self):
        monitors = self.get_available_monitors()
        self.monitor_dropdown.clear()
        for display_name, display_value in monitors:
            self.monitor_dropdown.addItem(display_name, display_value)

    def create_ui(self):
        self.layout.addWidget(QLabel("Monitor:"))
        self.monitor_dropdown = QComboBox()
        self.layout.addWidget(self.monitor_dropdown)

        refresh_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh Monitors")
        self.refresh_button.clicked.connect(self.populate_monitors)
        refresh_layout.addWidget(self.refresh_button)
        refresh_layout.addStretch()
        self.layout.addLayout(refresh_layout)

        self.layout.addWidget(QLabel("Resolution:"))
        self.resolution_dropdown = QComboBox()
        self.resolution_dropdown.addItems(["1920x1080", "1280x720", "640x480"])
        self.layout.addWidget(self.resolution_dropdown)

        self.layout.addWidget(QLabel("Frame Rate:"))
        self.framerate_dropdown = QComboBox()
        self.framerate_dropdown.addItems(["30", "60", "24"])
        self.layout.addWidget(self.framerate_dropdown)

        self.layout.addWidget(QLabel("Codec:"))
        self.codec_dropdown = QComboBox()
        self.codec_dropdown.addItems(["libx264", "libx265"])
        self.layout.addWidget(self.codec_dropdown)

        self.layout.addWidget(QLabel("CRF (Quality):"))
        self.crf_slider = QSlider(Qt.Horizontal)
        self.crf_slider.setRange(0, 51)
        self.crf_slider.setValue(23)
        self.layout.addWidget(self.crf_slider)

        self.audio_checkbox = QCheckBox("Record Audio")
        self.audio_checkbox.setChecked(True)
        self.layout.addWidget(self.audio_checkbox)

        self.remux_checkbox = QCheckBox("Remux to MP4 after recording")
        self.layout.addWidget(self.remux_checkbox)

        self.save_button = QPushButton("Select Save Location")
        self.save_button.clicked.connect(self.select_save_location)
        self.layout.addWidget(self.save_button)

        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Recording")
        self.start_button.clicked.connect(self.start_recording_thread)
        button_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Recording")
        self.stop_button.clicked.connect(self.stop_recording)
        button_layout.addWidget(self.stop_button)

        self.reset_button = QPushButton("Reset Settings")
        self.reset_button.clicked.connect(self.reset_settings)
        button_layout.addWidget(self.reset_button)

        self.layout.addLayout(button_layout)

        self.status_label = QLabel("Status: Ready")
        self.layout.addWidget(self.status_label)

    def select_save_location(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Save Location")
        if folder:
            self.save_location = folder
            self.status_label.setText(f"Save Location: {self.save_location}")
            self.settings.setValue("save_location", folder)

    def start_recording(self):
        resolution = self.resolution_dropdown.currentText()
        framerate = self.framerate_dropdown.currentText()
        codec = self.codec_dropdown.currentText()
        crf = self.crf_slider.value()
        audio_enabled = self.audio_checkbox.isChecked()
        selected_display = self.monitor_dropdown.currentData() or ":0.0"

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"REC_{timestamp}.mkv"
        output_file = os.path.join(self.save_location, file_name) if self.save_location else file_name

        command = [
            "ffmpeg", "-video_size", resolution, "-framerate", framerate,
            "-f", "x11grab", "-i", selected_display,
            "-c:v", codec, "-crf", str(crf), "-preset", "fast", output_file
        ]

        if audio_enabled:
            command.extend(["-f", "pulse", "-i", "default", "-c:a", "aac"])

        try:
            self.ffmpeg_process = subprocess.Popen(command)
            monitor_name = self.monitor_dropdown.currentText()
            self.status_label.setText(f"Recording {monitor_name}: {output_file}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start recording: {str(e)}")
            self.status_label.setText("Error: Failed to start recording")

        self.save_settings()

    def stop_recording(self):
        if self.ffmpeg_process:
            self.ffmpeg_process.terminate()
            self.ffmpeg_process = None
            self.status_label.setText("Recording stopped.")
            if self.remux_checkbox.isChecked():
                self.remux_to_mp4()

    def remux_to_mp4(self):
        if not self.save_location:
            QMessageBox.warning(self, "Error", "No save location selected.")
            return
        files = [f for f in os.listdir(self.save_location) if f.endswith(".mkv")]
        if not files:
            QMessageBox.warning(self, "Error", "No MKV file found to remux.")
            return
        last_recorded_file = max(files, key=lambda f: os.path.getctime(os.path.join(self.save_location, f)))
        input_path = os.path.join(self.save_location, last_recorded_file)
        output_path = input_path.replace(".mkv", ".mp4")
        command = ["ffmpeg", "-i", input_path, "-c", "copy", output_path]
        subprocess.run(command)
        self.status_label.setText(f"Remuxed to MP4: {output_path}")

    def start_recording_thread(self):
        thread = threading.Thread(target=self.start_recording)
        thread.start()

    def save_settings(self):
        self.settings.setValue("resolution", self.resolution_dropdown.currentText())
        self.settings.setValue("framerate", self.framerate_dropdown.currentText())
        self.settings.setValue("codec", self.codec_dropdown.currentText())
        self.settings.setValue("crf", self.crf_slider.value())
        self.settings.setValue("audio", self.audio_checkbox.isChecked())
        self.settings.setValue("remux", self.remux_checkbox.isChecked())
        self.settings.setValue("monitor", self.monitor_dropdown.currentIndex())
        if self.save_location:
            self.settings.setValue("save_location", self.save_location)

    def load_settings(self):
        self.resolution_dropdown.setCurrentText(self.settings.value("resolution", "1920x1080"))
        self.framerate_dropdown.setCurrentText(self.settings.value("framerate", "30"))
        self.codec_dropdown.setCurrentText(self.settings.value("codec", "libx264"))
        self.crf_slider.setValue(int(self.settings.value("crf", 23)))
        self.audio_checkbox.setChecked(self.settings.value("audio", True, type=bool))
        self.remux_checkbox.setChecked(self.settings.value("remux", False, type=bool))
        monitor_index = int(self.settings.value("monitor", 0))
        if 0 <= monitor_index < self.monitor_dropdown.count():
            self.monitor_dropdown.setCurrentIndex(monitor_index)
        self.save_location = self.settings.value("save_location", "")
        if self.save_location:
            self.status_label.setText(f"Save Location: {self.save_location}")

    def reset_settings(self):
        self.settings.clear()
        self.resolution_dropdown.setCurrentText("1920x1080")
        self.framerate_dropdown.setCurrentText("30")
        self.codec_dropdown.setCurrentText("libx264")
        self.crf_slider.setValue(23)
        self.audio_checkbox.setChecked(True)
        self.remux_checkbox.setChecked(False)
        if self.monitor_dropdown.count() > 0:
            self.monitor_dropdown.setCurrentIndex(0)
        self.save_location = ""
        self.status_label.setText("Settings reset to default")


def main():
    app = QApplication(sys.argv)
    window = ScreenRecorderApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
