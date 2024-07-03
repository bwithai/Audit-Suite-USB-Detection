from datetime import datetime
import os


def get_database_url(db_name="database.sqlite"):
    db_path = os.path.join("C:\\Windows\\System32")
    url = f"sqlite:///{db_path}\\{db_name}"
    return url


# def get_database_url():
#     url = "sqlite:///database.sqlite"
#     return url


def timestamp():
    # Get current time
    current_time = datetime.now()
    return current_time


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
