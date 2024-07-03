import os
import sys
import logging
import time

from PyQt5.QtWidgets import (QApplication, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
                             QPushButton, QDialog, QLabel, QHeaderView, QScrollArea, QSplitter, QSizePolicy, QTextEdit,
                             QHBoxLayout, QLineEdit, QMessageBox, QProgressBar, QFileDialog)
from PyQt5.QtGui import QFont, QIcon, QColor, QTextCharFormat, QTextCursor
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QRect, QEasingCurve, QSortFilterProxyModel, QDateTime, QThread, \
    pyqtSignal
from sqlmodel import Session

from database import crud
from database.db import create_db_and_tables, get_db, archive_db
from utils import stylesheet

# Setup logging
logging.basicConfig(level=logging.DEBUG)


class TableView(QDialog):
    def __init__(self, super_admin, admin, db, archive_view: bool = False, parent=None):
        super().__init__(parent)
        self.archive_db_path = None
        self.super_admin = super_admin
        self.admin = admin
        self.db = db
        self.archive_view = archive_view
        self.initUI()

    def initUI(self):
        # Set the window flags to include minimize and maximize buttons
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)

        if not self.archive_view:
            self.setWindowTitle('Device Table View')
        else:
            self.setWindowTitle('Archive Database View')

        self.setWindowIcon(QIcon('usb_logo.jpg'))

        layout = QVBoxLayout()

        self.table = QTableWidget()
        if (self.super_admin or self.admin) and not self.archive_view:
            self.table.setColumnCount(8)  # Set to 8 to include the "Register" column
            headers = ["Serial Number", "Device Name", "Device Manufacturer", "Media Information",
                       "Last Connected Time", "Last Removal Time", "More Info", "Register"]
        else:
            self.table.setColumnCount(7)
            headers = ["Serial Number", "Device Name",
                       "Device Manufacturer", "Media Information",
                       "Last Connected Time", "Last Removal Time", "More Info"]

        self.table.setHorizontalHeaderLabels(headers)

        # Bold the header
        header_font = QFont()
        header_font.setPointSize(12)
        header_font.setBold(True)

        # Ensure header items are created before setting the font
        for idx in range(len(headers)):
            item = QTableWidgetItem(headers[idx])
            item.setFont(header_font)
            self.table.setHorizontalHeaderItem(idx, item)

        header = self.table.horizontalHeader()

        # Set font size and padding for table items
        item_font = QFont()
        item_font.setPointSize(12)  # Adjust font size as needed
        self.table.setFont(item_font)
        self.table.verticalHeader().setDefaultSectionSize(40)  # Adjust row height as needed

        # Example data
        try:
            detected_devices = crud.get_latest_unique_detections(self.db)
        except Exception as e:
            logging.error(f"Error fetching detected devices: {e}")
            detected_devices = []

        # data = []
        # for device_info, tree in detected_devices:
        #     data.append(device_info)

        self.table.setRowCount(len(detected_devices))
        for row_idx, (row_data, tree, is_register) in enumerate(detected_devices):
            if is_register:
                bg_color = QColor(255, 255, 255)  # Default to white background
            else:
                bg_color = QColor(255, 150, 150)  # Light red color
            self.addTableItem(row_idx, 0, row_data["Serial Number"], bg_color)
            self.addTableItem(row_idx, 1, row_data["Device Display Name"], bg_color)
            self.addTableItem(row_idx, 2, row_data["Device Manufacture Name"], bg_color)
            self.addTableItem(row_idx, 3, row_data["Device Connect Through"], bg_color)
            self.addTableItem(row_idx, 4, row_data["Insertion Time"], bg_color)
            self.addTableItem(row_idx, 5, row_data["Removal Time"], bg_color)

            more_info_button = QPushButton("More Info")
            more_info_button.clicked.connect(lambda checked, r=row_data["Serial Number"]: self.showMoreInfo(r))
            self.table.setCellWidget(row_idx, 6, more_info_button)

            if (self.super_admin or self.admin) and not self.archive_view:
                register_usb_button = QPushButton("Register")
                register_usb_button.clicked.connect(lambda checked, r=row_data["Serial Number"]: self.register_usb(r))
                self.table.setCellWidget(row_idx, 7, register_usb_button)

        # Enable horizontal scrolling
        self.table.setHorizontalScrollMode(QTableWidget.ScrollPerPixel)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # Set Device Manufacturer column to Interactive for flexible resizing
        for i in range(3):
            header.setSectionResizeMode(i, QHeaderView.Interactive)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.table)
        layout.addWidget(scroll_area)

        if (self.super_admin or self.admin) and not self.archive_view:
            # Buttons layout
            buttons_layout = QHBoxLayout()

            archive_button = QPushButton("Archive Existing Data")
            archive_button.clicked.connect(self.show_archive_view)
            buttons_layout.addWidget(archive_button)

            view_archive_button = QPushButton("View Archive Data")
            view_archive_button.clicked.connect(self.open_archive_data)
            buttons_layout.addWidget(view_archive_button)

            layout.addLayout(buttons_layout)

        self.setLayout(layout)
        self.resize(1900, 900)

        # After setting up the layout, resize each column to fit contents and make the header interactive
        for column in range(self.table.columnCount()):
            self.table.resizeColumnToContents(column)

        # Adjust each row height for better visibility
        for row in range(self.table.rowCount()):
            self.table.setRowHeight(row, 45)  # Adjust the height as needed

        # Apply fade-in animation
        self.fadeInAnimation = QPropertyAnimation(self, b"windowOpacity")
        self.fadeInAnimation.setDuration(200)
        self.fadeInAnimation.setStartValue(0)
        self.fadeInAnimation.setEndValue(1)
        self.fadeInAnimation.setEasingCurve(QEasingCurve.InOutCubic)
        self.fadeInAnimation.start()

    def open_archive_data(self):
        self.show_archive_data_dialog = ShowArchiveData(self)
        self.show_archive_data_dialog.valueSelected.connect(self.handle_archive_db_path)
        self.show_archive_data_dialog.exec_()

    def handle_archive_db_path(self, value):
        self.archive_db_path = value
        self.close()
        self.restart_table_view()

    def restart_table_view(self):
        ar_db: Session = archive_db(self.archive_db_path)
        new_dialog = TableView(self.super_admin, self.admin, ar_db, archive_view=True)
        new_dialog.exec_()

    def show_archive_view(self):
        dialog = ArchiveView(self)
        if dialog.exec_() == QDialog.Accepted:
            logging.info("ArchiveView dialog accepted")

    def addTableItem(self, row, column, text, bg_color=None):
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignCenter)
        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)  # Set the item to be selectable but not editable
        if bg_color:
            item.setBackground(bg_color)
        self.table.setItem(row, column, item)

    def showMoreInfo(self, serial_number):
        dialog = MoreInfoDialog(serial_number, self.super_admin, self.db)
        dialog.exec_()

    def register_usb(self, serial_number):
        try:
            crud.register_usb(serial_number, self.db)
            self.show_message("Success", "USB has been successfully registered.")
            self.close()
            new_dialog = TableView(self.super_admin, self.admin, self.db)
            new_dialog.exec_()
        except Exception as e:
            self.show_message("Error", f"Failed to register USB: {str(e)}")

    def show_message(self, title, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()


class ShowArchiveData(QDialog):
    valueSelected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.path = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('View Archive Database')
        self.setWindowIcon(QIcon('usb_logo.jpg'))

        layout = QVBoxLayout()

        # Header
        header_label = QLabel("\nView Archive database\n")
        header_label.setObjectName("header")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setFont(QFont("Arial", 30, QFont.Bold))
        layout.addWidget(header_label)

        buttons_layout = QHBoxLayout()

        login_button = QPushButton("Select Archive Database file")
        login_button.clicked.connect(self.proceed)
        buttons_layout.addWidget(login_button)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)
        self.resize(700, 300)

    def proceed(self):
        file, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                              "All Files (*);;Python Files (*.py)")

        self.path = file

        if not self.path:
            QMessageBox.warning(self, "Archive Path", "Please select archive database file")
            return
        if os.path.isfile(self.path):
            self.valueSelected.emit(self.path)
            self.accept()
        else:
            QMessageBox.warning(self, "Archive Path", "Archive path does not contain any Database file")
            return

    def send_value(self):
        archive_db_path = self.path  # Replace this with actual logic to select the path
        self.valueSelected.emit(archive_db_path)
        self.accept()


class ArchiveWorker(QThread):
    update_progress = pyqtSignal(int)
    process_finished = pyqtSignal()

    def __init__(self, path, days, delete_old):
        super().__init__()
        self.path = path
        self.days = days
        self.delete_old = delete_old

    def run(self):
        crud.archive(self.path, self.days, self.delete_old, self.update_progress, self.process_finished)

    def archive_data(self):
        print(f"Path: {self.path}, Days: {self.days}, Delete Old: {self.delete_old}")
        # Perform the actual archiving logic here
        # QMessageBox.information(None, "Archive Complete",
        #                         f"Data archived successfully. Delete old data: {self.delete_old}")


class ArchiveView(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.path_input = None
        self.initUI()

    def initUI(self):
        # Set the window flags to include minimize and maximize buttons
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)

        self.setWindowTitle('Archive Database')
        self.setWindowIcon(QIcon('usb_logo.jpg'))

        layout = QVBoxLayout()

        # Header
        header_label = QLabel("\nArchive existing database\n")
        header_label.setObjectName("header")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setFont(QFont("Arial", 30, QFont.Bold))
        layout.addWidget(header_label)

        # Days input
        self.day_input = QLineEdit()
        self.day_input.setPlaceholderText("Enter number of days to archive")
        self.day_input.setFont(QFont("Arial", 20))
        layout.addWidget(self.day_input)

        # Progress bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Buttons layout
        buttons_layout = QHBoxLayout()

        self.archive_button = QPushButton("Archive")
        self.archive_button.clicked.connect(self.on_archive_button_clicked)
        buttons_layout.addWidget(self.archive_button)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)
        self.resize(700, 300)

    def on_archive_button_clicked(self):
        days_str = self.day_input.text()
        try:
            days = int(days_str)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter a valid number of days.")
            return

        self.path_input = QFileDialog.getExistingDirectory(self, "Select Directory to Store Archive Database")
        if not self.path_input:
            QMessageBox.warning(self, "Input Error", "Please select a path to store the archive database.")
            return

        # Ask for user permission to delete old data
        reply = QMessageBox.question(self, 'Delete Old Data',
                                     "Do you want to delete old data after archiving?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        delete_old = reply == QMessageBox.Yes

        self.archive_button.setEnabled(False)  # Disable the button during the process
        self.progress_bar.setValue(0)  # Reset the progress bar
        self.thread = ArchiveWorker(self.path_input, days, delete_old)
        self.thread.update_progress.connect(self.progress_bar.setValue)
        self.thread.process_finished.connect(self.on_process_finished)
        self.thread.start()

    def on_process_finished(self):
        self.archive_button.setEnabled(True)  # Enable the button after the process
        QMessageBox.information(self, "Process Complete", "Archiving process completed.")
        self.accept()


class MoreInfoDialog(QDialog):
    def __init__(self, serial_number, super_admin, db, parent=None):
        super().__init__(parent)

        # Set the window flags to include minimize and maximize buttons
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)

        self.super_admin = super_admin
        self.db = db
        self.setWindowTitle('More Info')
        self.setGeometry(100, 100, 1900, 900)  # Increase the size as needed

        layout = QVBoxLayout()

        # Create a new table widget for the popup window
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        headers = ["Serial Number", "Device Name", "Media Information",
                   "Connect Time", "Removal Time", "More Info"]
        self.table.setHorizontalHeaderLabels(headers)

        # Bold the header
        header_font = QFont()
        header_font.setPointSize(12)
        header_font.setBold(True)
        for idx in range(len(headers)):
            self.table.horizontalHeaderItem(idx).setFont(header_font)

        # Set font size and padding for table items
        item_font = QFont()
        item_font.setPointSize(12)  # Adjust font size as needed
        self.table.setFont(item_font)
        self.table.verticalHeader().setDefaultSectionSize(40)  # Adjust row height as needed

        # Enable sorting
        self.table.setSortingEnabled(True)

        try:
            detected_devices = crud.get_device_from_db(serial_number, self.db)
        except Exception as e:
            logging.error(f"Error fetching device data for serial number {serial_number}: {e}")
            detected_devices = []

        self.table.setRowCount(len(detected_devices))
        for row_idx, (row_data, tree, logs) in enumerate(detected_devices):
            self.addTableItem(row_idx, 0, row_data["Serial Number"])
            self.addTableItem(row_idx, 1, row_data["Device Display Name"])
            self.addTableItem(row_idx, 2, row_data["Device Connect Through"])
            self.addTableItem(row_idx, 3, row_data["Insertion Time"])
            self.addTableItem(row_idx, 4, row_data["Removal Time"])

            button = QPushButton("View Details")
            button.clicked.connect(lambda checked, rd=row_data, t=tree, l=logs: self.showDetails(rd, t, l))
            self.table.setCellWidget(row_idx, 5, button)

        # Expand columns to fit content
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.table)
        self.setLayout(layout)

        self.window_animation = QPropertyAnimation(self, b"geometry")
        self.window_animation.setDuration(300)
        self.window_animation.setEasingCurve(QEasingCurve.InOutCubic)

    def addTableItem(self, row, column, text):
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignCenter)
        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)  # Set the item to be selectable but not editable
        self.table.setItem(row, column, item)

    def showDetails(self, row_data, tree, logs):
        # Implement detail view logic here
        detail_dialog = DetailDialog(row_data, tree, logs, self.super_admin)
        detail_dialog.exec_()

    def showEvent(self, event):
        super().showEvent(event)
        self.window_animation.setStartValue(
            QRect(self.geometry().x(), self.geometry().y() - 50, self.width(), self.height()))
        self.window_animation.setEndValue(self.geometry())
        self.window_animation.start()

    def hideEvent(self, event):
        super().hideEvent(event)
        self.window_animation.setStartValue(self.geometry())
        self.window_animation.setEndValue(
            QRect(self.geometry().x(), self.geometry().y() - 50, self.width(), self.height()))
        self.window_animation.start()


class DetailDialog(QDialog):
    def __init__(self, row_data, tree, logs, super_admin, parent=None):
        super().__init__(parent)

        # Set the window flags to include minimize and maximize buttons
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)

        self.super_admin = super_admin
        if self.super_admin:
            self.logs = logs
        else:
            self.logs = ""
        self.setWindowTitle('Device Detail')
        self.setGeometry(100, 100, 1900, 950)  # Adjust size as needed

        main_layout = QVBoxLayout()

        # Create a splitter to hold table and tree structure
        splitter = QSplitter(Qt.Horizontal)

        keys_to_display = [
            'Storage Capacity',
            'Free Space',
            'Used Space',
            'Type of Storage',
            'Number of Partitions',
            'Capabilities of the drive',
            'Manufacture',
            'FirmwareRevision'
        ]

        # Create a widget for the details and add it to the splitter
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)

        # Header
        header_label = QLabel("\nDrive Information\n")
        header_label.setObjectName("header")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setFont(QFont("Arial", 22, QFont.Bold))
        header_label.setStyleSheet(
            "background-color: #006600; border-bottom: 1px solid #a0a0a0;")
        details_layout.addWidget(header_label)

        # Space & Access right Header
        sa_header = QLabel("Space & Access right")
        sa_header.setFont(QFont("Arial", 18))
        sa_header.setStyleSheet("font-weight: bold;")
        details_layout.addWidget(sa_header)

        # Initialize an empty string for the text display
        sa_display_text = ""

        # Add each key-value pair to the display text
        for key in keys_to_display:
            if key in row_data:
                if "Capabilities of the drive" in key:
                    value = row_data[key]
                    val = ""
                    for v in value:
                        val += "    - " + v + "\n"
                    sa_display_text += f"Drive Access Rights:\n\n{val}\n"
                else:
                    value = row_data[key]
                    sa_display_text += f"{key}: {value}\n"

        # Now add sa_text to the QTextEdit widget
        self.sa_text = QTextEdit()
        self.sa_text.setFont(QFont("Arial", 12))
        self.sa_text.setPlainText(sa_display_text)
        self.sa_text.setReadOnly(True)
        self.sa_text.setStyleSheet(
            "QTextEdit { background-color: #f0f0f0; border: 1px solid #ccc; padding: 10px; }")
        details_layout.addWidget(self.sa_text)

        log_lines = self.logs.split('\n')
        has_created = any("Created" in line for line in log_lines)
        has_deleted = any("Deleted" in line for line in log_lines)
        has_modified = any("Modified" in line or "Changed" in line for line in log_lines)

        if has_created:
            # Create sections for each log type
            self.create_log_section("Created Files Record", details_layout)
            self.created_logs = self.create_log_text_edit(details_layout)

        if has_deleted:
            self.create_log_section("Deleted Files Record", details_layout)
            self.deleted_logs = self.create_log_text_edit(details_layout)

        if has_modified:
            self.create_log_section("Modified Files Record", details_layout)
            self.modified_moved_logs = self.create_log_text_edit(details_layout)

        # Total Transferred Label
        self.total_label = QLabel("Total transferred: 0 MB")
        self.total_label.setFont(QFont("Arial", 14))
        details_layout.addWidget(self.total_label)

        splitter.addWidget(details_widget)

        # Create a widget for the tree structure and add it to the splitter
        tree_widget = QWidget()
        tree_layout = QVBoxLayout(tree_widget)

        drive_tree_label = QLabel("\nDrive Files Tree Structure\n")
        drive_tree_label.setObjectName("header")
        drive_tree_label.setAlignment(Qt.AlignCenter)
        drive_tree_label.setFont(QFont("Arial", 22, QFont.Bold))
        drive_tree_label.setStyleSheet("background-color: #006600; border-bottom: 1px solid #a0a0a0;")
        tree_layout.addWidget(drive_tree_label)

        tree_label = QLabel(f"{tree}")
        tree_label.setFont(QFont("Arial", 13))
        scroll_area = QScrollArea()
        scroll_area.setWidget(tree_label)
        scroll_area.setWidgetResizable(True)
        tree_layout.addWidget(scroll_area)

        tree_widget.setVisible(True)  # Initially hide the tree widget

        splitter.addWidget(tree_widget)

        # Set an initial size for the tree widget to make the splitter start from the center
        splitter.setSizes([self.width() // 2, self.width() // 2])

        # Add a button to show/hide the tree structure
        toggle_button = QPushButton("Hide Tree Structure")
        toggle_button.setObjectName("toggleButton")
        toggle_button.setCheckable(True)
        toggle_button.setChecked(False)
        toggle_button.toggled.connect(lambda checked: self.toggleTreeVisibility(tree_widget, toggle_button))

        main_layout.addWidget(splitter)
        main_layout.addWidget(toggle_button)
        self.setLayout(main_layout)

        # Apply fade-in animation
        self.fadeInAnimation = QPropertyAnimation(self, b"windowOpacity")
        self.fadeInAnimation.setDuration(200)
        self.fadeInAnimation.setStartValue(0)
        self.fadeInAnimation.setEndValue(1)
        self.fadeInAnimation.setEasingCurve(QEasingCurve.InOutCubic)
        self.fadeInAnimation.start()

        self.load_logs()

    def create_log_section(self, header_text, layout):
        header = QLabel(header_text)
        header.setFont(QFont("Arial", 14))
        layout.addWidget(header)

    def create_log_text_edit(self, layout):
        log_text_edit = QTextEdit()
        log_text_edit.setFont(QFont("Arial", 12))
        log_text_edit.setReadOnly(True)
        log_text_edit.setStyleSheet(
            "QTextEdit { background-color: #f0f0f0; border: 1px solid #ccc; padding: 10px; }")
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(log_text_edit)
        layout.addWidget(scroll_area)
        return log_text_edit

    def load_logs(self):

        log_lines = self.logs.split('\n')
        for line in log_lines:
            if "Created" in line:
                self.append_colored_text(line, QColor("dark green"), self.created_logs)
            elif "Deleted" in line:
                self.append_colored_text(line, QColor("dark red"), self.deleted_logs)
            elif "Modified" in line:
                self.append_colored_text(line, QColor("dark blue"), self.modified_moved_logs)
            elif "Changed" in line:
                self.append_colored_text(line, QColor("dark orange"), self.modified_moved_logs)
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

    def toggleTreeVisibility(self, tree_widget, toggle_button):
        if toggle_button.isChecked():
            tree_widget.setVisible(False)
            toggle_button.setText("Show Tree Structure")
        else:
            tree_widget.setVisible(True)
            toggle_button.setText("Hide Tree Structure")


if __name__ == '__main__':
    create_db_and_tables()
    db: Session = get_db()
    app = QApplication(sys.argv)
    app.setStyleSheet(stylesheet)
    ex = TableView(True, False, db)
    ex.show()
    sys.exit(app.exec_())
