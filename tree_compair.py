import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QHBoxLayout
from PyQt5.QtGui import QColor, QTextCursor, QTextCharFormat, QIcon
import difflib

tree1 = """project/
├── src/
│   ├── main.py
│   ├── utils.py
│   └── __init__.py
├── tests/
│   ├── test_main.py
│   └── test_utils.py
├── data/
│   ├── input.txt
│   └── output.txt
├── docs/
│   └── README.md
└── setup.py
"""

tree2 = """project/
├── src/
│   ├── main.py
│   ├── utils.py
│   └── __init__.py
├── tests/
│   ├── test_main.py
│   └── test_utils.py
├── docs/
│   └── README.md
├── src/
│   ├── main.py
│   ├── utils.py
│   └── __init__.py
└── setup.py
"""

def find_differences(tree1, tree2):
    diff = difflib.unified_diff(tree1.splitlines(), tree2.splitlines(), lineterm='')
    return list(diff)

class TreeComparisonApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Set window properties
        self.setWindowTitle('Tree Comparison')
        self.setWindowIcon(QIcon('usb_logo.jpg'))
        self.setGeometry(100, 100, 800, 600)

        # Layouts
        main_layout = QVBoxLayout()

        # Insertion Tree Header
        insertion_tree_header = QLabel("Insertion Tree")
        insertion_tree_header.setStyleSheet("font-weight: bold; font-size: 16px;")
        main_layout.addWidget(insertion_tree_header)

        # Tree1 TextEdit
        self.tree1_text = QTextEdit()
        self.tree1_text.setPlainText(tree1)
        self.tree1_text.setReadOnly(True)
        self.tree1_text.setStyleSheet("QTextEdit { background-color: #f0f0f0; border: 1px solid #ccc; padding: 10px; }")
        main_layout.addWidget(self.tree1_text)

        # Removal Tree Header
        removal_tree_header = QLabel("Removal Tree")
        removal_tree_header.setStyleSheet("font-weight: bold; font-size: 16px;")
        main_layout.addWidget(removal_tree_header)

        # Tree2 TextEdit
        self.tree2_text = QTextEdit()
        self.tree2_text.setPlainText(tree2)
        self.tree2_text.setReadOnly(True)
        self.tree2_text.setStyleSheet("QTextEdit { background-color: #f0f0f0; border: 1px solid #ccc; padding: 10px; }")
        main_layout.addWidget(self.tree2_text)

        # Difference TextEdit
        self.diff_text = QTextEdit()
        self.diff_text.setReadOnly(True)
        self.diff_text.setStyleSheet("QTextEdit { background-color: #ffffff; border: 1px solid #ccc; padding: 10px; }")
        main_layout.addWidget(QLabel("Differences:"))
        main_layout.addWidget(self.diff_text)

        # Compare Button
        self.compare_button = QPushButton('Compare')
        self.compare_button.setStyleSheet("QPushButton { padding: 10px; background-color: #4CAF50; color: white; border: none; }")
        self.compare_button.clicked.connect(self.compare_trees)
        main_layout.addWidget(self.compare_button)

        self.setLayout(main_layout)

    def compare_trees(self):
        differences = find_differences(tree1, tree2)
        self.diff_text.clear()
        cursor = self.diff_text.textCursor()
        for line in differences:
            color = None
            if line.startswith('+'):
                color = QColor('#228B22')  # Green for additions
            elif line.startswith('-'):
                color = QColor('#B22222')  # Red for deletions
            elif line.startswith('@'):
                color = QColor('#0000FF')  # Blue for context information
            else:
                color = QColor('#000000')  # Black for unchanged lines

            self.append_colored_text(cursor, line, color)

    def append_colored_text(self, cursor, text, color):
        format = QTextCharFormat()
        format.setForeground(color)
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text + '\n', format)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TreeComparisonApp()
    ex.show()
    sys.exit(app.exec_())
