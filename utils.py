from datetime import datetime
import os
import base64


def image_to_base64(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    else:
        print(f"Image path {image_path} does not exist.")
        return None


def get_database_url():
    url = "sqlite:///database.sqlite"
    return url


# def timestamp():
#     # Get current time
#     current_time = datetime.now()
#
#     # Format the current time
#     current_time_formatted = current_time.strftime("%m/%d/%Y - %I:%M %p")
#
#     return current_time_formatted

def timestamp():
    # Get current time
    current_time = datetime.now()
    return current_time


def get_time(epoch_time):
    # Convert to a human-readable format
    human_readable_time = datetime.datetime.fromtimestamp(epoch_time / 10 ** 7)

    # Subtract 369 years from the year part of the timestamp
    adjusted_time = human_readable_time.replace(year=human_readable_time.year - 369)

    # Format the adjusted time
    adjusted_time_formatted = adjusted_time.strftime("%m/%d/%Y - %I:%M %p")

    # Print the adjusted time in the desired format
    return adjusted_time_formatted


def bytes_to_gb(bytes):
    gb = bytes / (1024 ** 3)
    return gb


def print_tree(directory, tree, indent='', last=True):
    # Add the current directory or file to the tree string
    tree += indent
    if last:
        tree += '└── '
        indent += '    '
    else:
        tree += '├── '
        indent += '│   '
    tree += os.path.basename(directory) + '\n'

    # Iterate over the contents of the directory

    contents = os.listdir(directory)
    for i, item in enumerate(contents):
        item_path = os.path.join(directory, item)
        is_last = (i == len(contents) - 1)

        # Check if the item is a directory
        if os.path.isdir(item_path):
            if "System Volume Information" in item_path:
                continue
            # If it's a directory, recursively add its contents to the tree string
            tree = print_tree(item_path, tree, indent, is_last)
        else:
            # If it's a file, print its name
            tree += indent
            if is_last:
                tree += '└── '
            else:
                tree += '├── '
            tree += item + "\n"
            # If it's a file, add its name to the tree string
            # tree += indent + ('└── ' if is_last else '├── ') + item + '\n'

    return tree


# Example
# directory = 'E:'
# tree = print_tree(directory, 'E:\n')
# print(tree)


image_path = 'C:/Office/audit_suite/usb_logo.jpg'

stylesheet = f"""
/* styles.css */

/* TableView */
QTableWidget {{
    background-color: #f0f0f0;
}}

QTableWidget QHeaderView::section {{
    background-color: #006600;
    color: white;
    padding: 15px;
    border: 1px solid #a0a0a0;
}}

QTableWidget QPushButton {{
    background-color: #003300;
    color: white;
    border: 2px solid #006600; 
    padding: 8px 16px;
    text-align: center;
    text-decoration: none;
    display: inline-block;
    font-size: 14px;
    margin: 4px 2px;
    transition-duration: 0.4s;
    cursor: pointer;
}}

QTableWidget QPushButton:hover {{
    background-color: #006600; /* Darker blue color on hover */
    border-color: #0056b3; /* Darker border color on hover */
}}

/* MoreInfoDialog */
MoreInfoDialog {{
    background-color: #f0f0f0;
}}

MoreInfoDialog QPushButton {{
    background-color: #003300;
    color: white;
    border: 2px solid #006600;
    padding: 8px 16px;
    text-align: center;
    text-decoration: none;
    display: inline-block;
    font-size: 14px;
    margin: 4px 2px;
    transition-duration: 0.4s;
    cursor: pointer;
}}

MoreInfoDialog QPushButton:hover {{
    background-color: #006600;
    border-color: #0056b3;
}}

/* DetailDialog */
DetailDialog {{
    background-color: #f0f0f0;
}}

DetailDialog QPushButton#toggleButton {{
    background-color: #003300;
    color: white;
    border: 2px solid #006600;
    padding: 8px 16px;
    text-align: center;
    text-decoration: none;
    display: inline-block;
    font-size: 14px;
    margin: 4px 2px;
    transition-duration: 0.4s;
    cursor: pointer;
}}

DetailDialog QPushButton#toggleButton:hover {{
    background-color: #006600;
    border-color: #0056b3;
}}

/* General styles */
QWidget {{
    background-color: #f5f5f5;
    color: #333;
    font-family: Arial;
}}

/* Header styles */
#header {{
    background-color: #006600;
    background-image: url("data:image/jpg;base64,{image_to_base64(image_path)}");
    color: #ffffff;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
    background-repeat: no-repeat;
    background-position: center;
}}

/* Input fields */
QLineEdit {{
    border: 2px solid #d0d0d0;
    border-radius: 10px;
    padding: 10px;
    font-size: 18px;
    background-color: #ffffff;
    transition: border-color 0.3s ease, box-shadow 0.3s ease;
}}

QLineEdit:focus {{
    border-color: #3a3a3a;
    box-shadow: 0 0 10px #3a3a3a;
}}

/* Buttons */
QPushButton {{
    background-color: #003300;
    color: #ffffff;
    border: 2px solid #3a3a3a;
    border-radius: 10px;
    padding: 10px 10px;
    font-size: 18px;
    transition: background-color 0.3s ease, color 0.3s ease, transform 0.3s ease;
}}

QPushButton:hover {{
    background-color: #006600;
    color: #ffffff;
    transform: scale(1.05);
}}

QPushButton:pressed {{
    background-color: #2a2a2a;
    color: #ffffff;
    transform: scale(0.95);
}}
"""
