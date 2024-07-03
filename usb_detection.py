import pprint

import win32api
import win32con
import win32gui
import threading
import pythoncom
import usb_monitoring
from sqlmodel import Session
from database.db import get_db, create_db_and_tables
from log_watcher import start_monitoring
from utils import print_tree, timestamp
from database import crud

connected_devices = usb_monitoring.get_connected_devices()
disks = usb_monitoring.get_existing_disk()
monitor_threads = {}


def extract_new_devices():
    global connected_devices
    current_devices = usb_monitoring.get_connected_devices()
    new_devices = {sn: dev for sn, dev in current_devices.items() if sn not in connected_devices}
    return new_devices, current_devices


def extract_new_disks():
    global disks
    current_disks = usb_monitoring.get_existing_disk()
    new_disks = {symbol: dev for symbol, dev in current_disks.items() if symbol not in disks}
    return new_disks, current_disks


def create_window() -> int:
    """
    Create a window for listening to messages
    """
    wc = win32gui.WNDCLASS()
    wc.lpfnWndProc = wnd_proc
    wc.lpszClassName = 'USB Monitoring'
    wc.hInstance = win32api.GetModuleHandle(None)
    class_atom = win32gui.RegisterClass(wc)
    return win32gui.CreateWindow(class_atom, 'USB Monitoring', 0, 0, 0, 0, 0, 0, 0, wc.hInstance, None)


def wnd_proc(hwnd, msg, wparam, lparam):
    """
    Window procedure to handle messages
    """
    if msg == win32con.WM_DEVICECHANGE:
        if wparam == win32con.DBT_DEVICEARRIVAL:
            print("USB device connected")
            # Start a new thread to extract device information
            threading.Thread(target=connection_monitoring).start()
        elif wparam == win32con.DBT_DEVICEREMOVECOMPLETE:
            # USB device removed
            print("USB device removed")
            threading.Thread(target=removal_monitoring).start()
    return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)


def connection_monitoring():
    print("thread is started")
    global connected_devices
    global disks
    global monitor_threads
    """
    Extract information about connected USB devices
    """
    try:
        # Initialize the COM environment
        pythoncom.CoInitialize()

        new_devices, current_devices = extract_new_devices()
        new_disks, current_disks = extract_new_disks()
        if new_devices:
            tree = ''
            symbol = ''
            try:
                symbol, drive = next(iter(new_disks.items()))
            except Exception as e:
                print("Win32_LogicalDisk for new drive give: ", str(e))
            try:
                tree = print_tree(symbol, symbol + '\n')
                monitor_threads[symbol] = start_monitoring(symbol)
            except Exception as e:
                print(f"tree on {symbol} give: ", str(e))

            serial_number, device = next(iter(new_devices.items()))
            if drive['name'] == '':
                drive['name'] = f'USB Drive ({symbol})'
            device['display_name'] = drive['name']
            device['total_size'] = drive['total_size']
            device['free_space'] = drive['free_space']
            device['used_space'] = drive['used_space']
            crud.add_or_update_detected_pc(device, serial_number, tree, timestamp())

        connected_devices = current_devices
        disks = current_disks

        # Uninitialize the COM environment
        pythoncom.CoUninitialize()
    except Exception as e:
        print("Error:", e)


def removal_monitoring():
    print("thread is started")
    global connected_devices
    global disks
    """
    Extract information about connected USB devices
    """
    try:
        # Initialize the COM environment
        pythoncom.CoInitialize()

        current_devices = usb_monitoring.get_connected_devices()
        removal_device = {sn: dev for sn, dev in connected_devices.items() if sn not in current_devices}
        serial_number, device = next(iter(removal_device.items()))

        current_disks = usb_monitoring.get_existing_disk()
        removal_disk = {symbol: dev for symbol, dev in disks.items() if symbol not in current_disks}

        logs = ''
        try:
            symbol, drive = next(iter(removal_disk.items()))
            logs = monitor_threads[symbol].stop()
        except Exception as e:
            print("Win32_LogicalDisk for removal drive give: ", str(e))

        crud.update_removal_time(serial_number, timestamp(), logs)

        connected_devices = current_devices
        disks = current_disks
        print("removed device is also removed from database")

        # Uninitialize the COM environment
        pythoncom.CoUninitialize()
    except Exception as e:
        print("Error:", e)


if __name__ == '__main__':
    # Create a database session
    db: Session = get_db()
    create_db_and_tables()
    hwnd = create_window()
    win32gui.PumpMessages()
