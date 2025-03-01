import sys
import os
import psutil
import shutil
import win32com.client
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QTextEdit, QFileDialog, QGridLayout, QHBoxLayout, QComboBox
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

class FileEventHandler(FileSystemEventHandler):
    def __init__(self, output_widget):
        super().__init__()
        self.output_widget = output_widget

    def on_deleted(self, event):
        if not event.is_directory:
            self.output_widget.append(f"❌ File Deleted: {event.src_path}")

class FileSystemTool(QWidget):
    def __init__(self):
        super().__init__()
        self.folder_to_monitor = None
        self.observer = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Advanced File System Recovery & Optimization Tool")
        self.setGeometry(100, 100, 900, 600)
        self.setStyleSheet("background-color: #e6f7ff; color: #333;")
        self.setWindowIcon(QIcon("icon.png"))

        layout = QVBoxLayout()
        title = QLabel("📂 Advanced File System Recovery & Optimization Tool")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #0056b3; padding: 10px;")
        layout.addWidget(title)

        self.drive_selector = QComboBox()
        self.drive_selector.addItem("Select a Drive")
        self.drive_selector.currentIndexChanged.connect(self.display_drive_files)
        layout.addWidget(self.drive_selector)
        
        button_layout = QGridLayout()
        buttons = {
            "Scan System": self.scan_files,
            "Monitor Files": self.monitor_files,
            "Recover Files": self.recover_deleted_files,
            "Optimize Storage": self.optimize_storage,
            "Select Folder": self.select_folder,
            "Clear Log": self.clear_output
        }

        row, col = 0, 0
        for text, function in buttons.items():
            btn = QPushButton(text)
            btn.setFont(QFont("Arial", 11, QFont.Bold))
            btn.setStyleSheet("background-color: #0056b3; color: white; padding: 12px; border-radius: 8px;")
            btn.clicked.connect(function)
            button_layout.addWidget(btn, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1

        layout.addLayout(button_layout)
        
        self.output_text = QTextEdit(readOnly=True)
        self.output_text.setStyleSheet("background-color: white; color: black; border: 2px solid #0056b3; padding: 10px; border-radius: 5px;")
        layout.addWidget(self.output_text)

        self.setLayout(layout)
        self.load_drives()

    def load_drives(self):
        self.drive_selector.clear()
        self.drive_selector.addItem("Select a Drive")
        for drive in [d.device for d in psutil.disk_partitions()]:
            self.drive_selector.addItem(drive)
    
    def display_drive_files(self):
        selected_drive = self.drive_selector.currentText()
        if selected_drive == "Select a Drive":
            return
        
        self.output_text.append(f"📂 Files in {selected_drive}:\n")
        for root, _, files in os.walk(selected_drive):
            for file in files:
                self.output_text.append(f"📄 {os.path.join(root, file)}")

    def scan_files(self):
        self.output_text.append("🔍 Scanning file system...\n")
        for drive in [d.device for d in psutil.disk_partitions()]:
            total, used, free = shutil.disk_usage(drive)
            old_files = []
            for root, _, files in os.walk(drive):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        last_access_time = os.path.getatime(file_path)
                        days_unused = (time.time() - last_access_time) // (24 * 3600)
                        if days_unused > 180:
                            size = os.path.getsize(file_path) // (1024**2)
                            old_files.append((file_path, days_unused, size))
                    except Exception:
                        continue

            self.output_text.append(f"✅ Drive: {drive} | Total: {total // (1024**3)}GB | Free: {free // (1024**3)}GB\n")
            for file_path, days, size in old_files:
                self.output_text.append(f"⚠️ Unused File: {file_path} | Last Accessed: {days} days ago | Size: {size} MB\n")

    def monitor_files(self):
        if not self.folder_to_monitor:
            self.output_text.append("⚠️ Please select a folder first!\n")
            return
        
        self.output_text.append(f"📂 Monitoring folder: {self.folder_to_monitor}\n")
        self.observer = Observer()
        self.observer.schedule(FileEventHandler(self.output_text), self.folder_to_monitor, recursive=True)
        self.observer.start()

    def recover_deleted_files(self):
        recovery_folder = QFileDialog.getExistingDirectory(self, "Select Recovery Folder")
        if not recovery_folder:
            self.output_text.append("⚠️ Recovery canceled!\n")
            return
        
        shell = win32com.client.Dispatch("Shell.Application")
        recycle_bin = shell.Namespace(10)
        
        for item in recycle_bin.Items():
            recovered_path = os.path.join(recovery_folder, item.Name)
            shutil.move(item.Path, recovered_path)
            self.output_text.append(f"🔄 Recovered: {item.Name} → {recovered_path}\n")
        
        self.output_text.append(f"✅ Files saved in: {recovery_folder}\n")

    def optimize_storage(self):
        self.output_text.append("🛠️ Optimizing storage...\n")
        os.system("cleanmgr /sagerun:1")
        self.output_text.append("✅ Optimization Complete!\n")

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.folder_to_monitor = folder
            self.output_text.append(f"📂 Selected Folder: {folder}\n")
    
    def clear_output(self):
        self.output_text.clear()
        self.output_text.append("🗑️ Log cleared!\n")

    def closeEvent(self, event):
        if self.observer:
            self.observer.stop()
            self.observer.join()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileSystemTool()
    window.show()
    sys.exit(app.exec_())