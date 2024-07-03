import time

import wmi

# Constants
REFRESH_INTERVAL = 1  # in seconds


def get_existing_disk():
    disks = {}
    c = wmi.WMI()
    for disk in c.Win32_LogicalDisk():
        device_id = disk.DeviceID
        volume_name = disk.VolumeName
        free_space_gb = round(int(disk.FreeSpace) / (1024 ** 3), 2)
        size_gb = round(int(disk.Size) / (1024 ** 3), 2)
        used_space_gb = round(size_gb - free_space_gb, 2)

        # Check if used space is less than 1 GB
        if used_space_gb < 1:
            used_space_mb = round((size_gb - free_space_gb) * 1024, 2)
            used_space_str = f"{used_space_mb} MB"
        else:
            used_space_str = f"{used_space_gb} GB"

        disk_info = {
            "name": volume_name,
            "free_space": f"{free_space_gb} GB",
            "total_size": f"{size_gb} GB",
            "used_space": used_space_str
        }

        disks[device_id] = disk_info

    return disks


def get_connected_devices():
    """
    Retrieve information about connected disk drives.

    Returns:
        dict: A dictionary containing SerialNumber as keys and corresponding disk drive objects as values.
    """
    try:
        connected_devices = {}
        c = wmi.WMI()
        for device in c.Win32_DiskDrive():
            device_info = {
                "SerialNumber": device.SerialNumber,
                "Caption": device.Caption,
                "InterfaceType": device.InterfaceType,
                "MediaType": device.MediaType,
                "Model": device.Model,
                "Status": device.Status,
                "Partitions": device.Partitions,
                "CapabilityDescriptions": device.CapabilityDescriptions,
                "Manufacturer": device.Manufacturer,
                "FirmwareRevision": device.FirmwareRevision
            }

            connected_devices[device.SerialNumber] = device_info
        return connected_devices
    except Exception as e:
        # Log the error instead of printing directly
        print(f"Error retrieving connected devices: {e}")
        return {}


def bytes_to_gb(bytes):
    gb = bytes / (1024 ** 3)
    return gb


def print_device_info(device, drive):
    """
    Print information about a given disk drive.

    Args:
        device (object): Disk drive object containing information.
    """
    try:
        print(f"Serial Number: {device.SerialNumber}")
        print(f"Device Name: {drive['name']}")
        print(f"Device Manufacture Name: {device.Caption}")
        print(f"Device Connect through: {device.InterfaceType}")
        # print(f"Storage Capacity: {bytes_to_gb(int(device.Size)):.2f} GB")
        print(f"Storage Capacity: {drive['total_size']}")
        print(f"Free Space: {drive['free_space']}")
        print(f"Used Space: {drive['used_space']}")
        print(f"Type of Storage: {device.MediaType}")
        print(f"Specific version or Model of the drive: {device.Model}")
        print(f"Drive Status: {device.Status}")
        print(f"number of partitions: {device.Partitions}")
        print(f"capabilities of the drive: {device.CapabilityDescriptions}")
        print(f"company that made the drive: {device.Manufacturer}")
        print(f"Software that controls the drive (FirmwareRevision): {device.FirmwareRevision}")
        # Add more properties as needed
        print("-" * 30)
    except Exception as e:
        # Log the error instead of printing directly
        print(f"Error printing device information: {e}")
        # \\.\PHYSICALDRIVE1


def monitor_usb_devices():
    """
    Monitor USB devices and print information about newly connected devices.
    """
    connected_devices = get_connected_devices()
    while True:
        try:
            time.sleep(REFRESH_INTERVAL)
            current_devices = get_connected_devices()
            new_devices = {sn: dev for sn, dev in current_devices.items() if sn not in connected_devices}

            for serial_number, device in new_devices.items():
                print("New USB device connected:")
                print_device_info(device)

            connected_devices = current_devices
        except KeyboardInterrupt:
            print("Monitoring stopped by user.")
            break
        except Exception as e:
            # Log the error instead of printing directly
            print(f"Error in monitoring: {e}")

# if __name__ == "__main__":
#     monitor_usb_devices()
