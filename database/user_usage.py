from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, QTextEdit, QLabel, QScrollArea)
from PyQt5.QtGui import QFont, QColor, QTextCursor, QTextCharFormat
from PyQt5.QtCore import Qt
import sys


class LogWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Log Viewer')
        self.setGeometry(100, 100, 800, 600)

        # Main widget and layout
        main_widget = QWidget()
        self.main_layout = QVBoxLayout(main_widget)
        self.setCentralWidget(main_widget)

        # Store created text edits for logs
        self.created_logs = None
        self.deleted_logs = None
        self.modified_moved_logs = None

        # Total Transferred Label
        self.total_label = QLabel("Total transferred: 0 MB")
        self.total_label.setFont(QFont("Arial", 14))
        self.main_layout.addWidget(self.total_label)

        self.load_logs()

    def create_log_section(self, header_text):
        header = QLabel(header_text)
        header.setFont(QFont("Arial", 18))
        header.setStyleSheet("font-weight: bold;")
        self.main_layout.addWidget(header)

    def create_log_text_edit(self):
        log_text_edit = QTextEdit()
        log_text_edit.setFont(QFont("Arial", 12))
        log_text_edit.setReadOnly(True)
        log_text_edit.setStyleSheet(
            "QTextEdit { background-color: #f0f0f0; border: 1px solid #ccc; padding: 10px; }")
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(log_text_edit)
        self.main_layout.addWidget(scroll_area)
        return log_text_edit

    def load_logs(self):
        logs = """[2024-06-10 14:17:02] Created: E:/usb_logger.exe, Size: 39.85 MB
Total transferred: 39.85 MB
[2024-06-10 14:17:58] Moved: E:/usb_logger - Copy.exe, Size: 39.85 MB
[2024-06-10 14:17:58] Moved: E:/usb_logger - Copy.exe, Size: 39.85 MB
[2024-06-10 14:17:58] Deleted: E:/usb_logger - Copy.exe, Size: 39.85 MB
Total transferred: 79.71 MB
[2024-06-10 14:18:28] Created: E:/USB Audit Suit\\usb_detection.exe, Size: 14.91 MB
Total transferred: 94.62 MB
[2024-06-10 14:18:29] Modified: E:/USB Audit Suit\\usb_detection_noconsole.exe, Size: 14.91 MB
Total transferred: 109.53 MB
[2024-06-10 14:18:29] Created: E:/USB Audit Suit\\usb_logger.exe, Size: 39.85 MB
Total transferred: 149.38 MB"""

        log_lines = logs.split('\n')
        has_created = any("Created" in line for line in log_lines)
        has_deleted = any("Deleted" in line for line in log_lines)
        has_modified_or_moved = any("Modified" in line or "Moved" in line for line in log_lines)

        if has_created:
            self.create_log_section("Created Files Record")
            self.created_logs = self.create_log_text_edit()

        if has_deleted:
            self.create_log_section("Deleted Files Record")
            self.deleted_logs = self.create_log_text_edit()

        if has_modified_or_moved:
            self.create_log_section("Modified and Moved Files Record")
            self.modified_moved_logs = self.create_log_text_edit()

        for line in log_lines:
            if "Created" in line and self.created_logs:
                self.append_colored_text(line, QColor("dark green"), self.created_logs)
            elif "Deleted" in line and self.deleted_logs:
                self.append_colored_text(line, QColor("dark red"), self.deleted_logs)
            elif ("Modified" in line or "Moved" in line) and self.modified_moved_logs:
                color = QColor("dark blue") if "Modified" in line else QColor("dark orange")
                self.append_colored_text(line, color, self.modified_moved_logs)
            elif "Total transferred" in line:
                self.total_label.setText(line)

    def append_colored_text(self, text, color, target_log):
        cursor = target_log.textCursor()
        cursor.movePosition(QTextCursor.End)

        format = QTextCharFormat()
        format.setForeground(color)
        cursor.insertText(text + "\n", format)
        target_log.setTextCursor(cursor)
        target_log.ensureCursorVisible()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LogWindow()
    window.show()
    sys.exit(app.exec_())
