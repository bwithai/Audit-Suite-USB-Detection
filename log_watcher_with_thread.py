import time
import os
import math
import threading
from datetime import datetime, timedelta
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class USBEventHandler(FileSystemEventHandler):
    def __init__(self):
        self.total_transferred = 0
        self.file_events = {}
        self.logs = []  # Store logs here

    def convert_size(self, size_bytes):
        if size_bytes == 0:
            return "0 B"
        size_name = ("B", "KB", "MB", "GB", "TB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_name[i]}"

    def log_event(self, action, path, size=None):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if size is not None:
            log_message = f"[{timestamp}] {action}: {path}, Size: {self.convert_size(size)}"
            self.logs.append(log_message)
            self.logs.append(f"Total transferred: {self.convert_size(self.total_transferred)}")
        else:
            log_message = f"[{timestamp}] {action}: {path}"
            self.logs.append(log_message)

    def on_created(self, event):
        if not event.is_directory:
            file_size = os.path.getsize(event.src_path)
            self.total_transferred += file_size
            self.file_events[event.src_path] = (datetime.now(), file_size, "created")
            self.log_event("Created", event.src_path, file_size)
        else:
            self.log_event("Created directory", event.src_path)

    def on_deleted(self, event):
        self.log_event("Deleted", event.src_path)
        if event.src_path in self.file_events:
            del self.file_events[event.src_path]

    def on_modified(self, event):
        if not event.is_directory:
            now = datetime.now()
            file_size = os.path.getsize(event.src_path)
            if event.src_path in self.file_events:
                last_event_time, last_size, last_event_type = self.file_events[event.src_path]
                if last_event_type == "created" and (now - last_event_time) < timedelta(seconds=5):
                    self.file_events[event.src_path] = (now, file_size, "modified")
                    return  # Skip logging if recently created
                if last_size == file_size:
                    self.file_events[event.src_path] = (now, file_size, "modified")
                    return  # Skip logging if the size has not changed

            self.total_transferred += file_size
            self.file_events[event.src_path] = (now, file_size, "modified")
            self.log_event("Modified", event.src_path, file_size)

    def on_moved(self, event):
        self.log_event("Changed", f"from {event.src_path} to {event.dest_path}")
        if event.src_path in self.file_events:
            self.file_events[event.dest_path] = self.file_events.pop(event.src_path)

    def get_logs(self):
        return "\n".join(self.logs)


class MonitorThread(threading.Thread):
    def __init__(self, drive_letter):
        super().__init__()
        self.drive_letter = drive_letter
        self.observer = Observer()
        self.event_handler = USBEventHandler()

    def run(self):
        # Schedule the event handler to monitor the specified drive
        self.observer.schedule(self.event_handler, path=self.drive_letter, recursive=True)
        self.observer.start()  # Start the observer to begin monitoring
        print(f"Monitoring started on {self.drive_letter}...")

    def stop(self):
        # Method to stop the observer from outside the thread
        self.observer.stop()
        self.observer.join()
        print(f"Monitoring stopped on {self.drive_letter}")
        return self.event_handler.get_logs()


def start_monitoring(drive_letter):
    monitor_thread = MonitorThread(drive_letter)
    monitor_thread.start()
    return monitor_thread


# if __name__ == "__main__":
#     drives_to_monitor = ["E:"]  # Replace with your drive letters
#     monitor_threads = {}
#
#     monitor_threads["E:"] = start_monitoring("E:")
#     input("ente:r: ")
#     print(monitor_threads)
#     logs = monitor_threads["E:"].stop()
#     del monitor_threads["E:"]
#     print(logs)
