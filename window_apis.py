import time

import wmi

c = wmi.WMI()

# for item in c.Win32_PhysicalMedia():
#     print(item)

# for drive in c.Win32_DiskDrive():
#     print(drive.SerialNumber)
    # 0101847c729ce5835dea


#
# for disk in c.Win32_LogicalDisk():
#     print(disk)

for disk in c.Win32_LogicalDisk():
    print(disk.Name)