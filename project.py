import sys
import os
import psutil
import shutil
import win32com.client
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QTextEdit, QFileDialog, QHBoxLayout, QFrame, QGridLayout
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon
from PyQt5.QtCore import Qt
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FileEventHandler(FileSystemEventHandler):
    def __init__(self, output_widget):
        super().__init__()
        self.output_widget = output_widget

    def on_created(self, event):
        if not event.is_directory:
            self.output_widget.append(f"🆕 File Created: {event.src_path}")

    def on_modified(self, event):
        if not event.is_directory:
            self.output_widget.append(f"✏️ File Modified: {event.src_path}")

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
        self.setWindowTitle("Smart File System Recovery & Optimization Tool")
        self.setGeometry(100, 100, 900, 600)
        self.setStyleSheet("background-color: #f4f4f4; color: #333;")
        self.setWindowIcon(QIcon("icon.png"))

        layout = QVBoxLayout()
        title = QLabel("📂 Smart File System Recovery & Optimization Tool")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #0056b3; padding: 10px;")
        layout.addWidget(title)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #0056b3; height: 2px;")
        layout.addWidget(separator)

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

    def scan_files(self):
        self.output_text.append("🔍 Scanning file system...\n")
        for drive in [d.device for d in psutil.disk_partitions()]:
            total, used, free = shutil.disk_usage(drive)
            self.output_text.append(f"✅ Drive: {drive} | Total: {total // (1024**3)}GB | Free: {free // (1024**3)}GB\n")

    def monitor_files(self):
        if not self.folder_to_monitor:
            self.output_text.append("⚠️ Please select a folder first!\n")
            return
        
        self.output_text.append(f"📂 Monitoring folder: {self.folder_to_monitor}\n")
        self.observer = Observer()
        self.observer.schedule(FileEventHandler(self.output_text), self.folder_to_monitor, recursive=True)
        self.observer.start()

    def recover_deleted_files(self):
        self.output_text.append("♻️ Recovering deleted files...\n")
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
