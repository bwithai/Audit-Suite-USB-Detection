import hashlib
from datetime import datetime, timedelta
from typing import Optional, Sequence

from sqlmodel import select, desc, func

import utils
from .db import Session, get_db, archive_db
from . import models
from .models import UserRegister


def copy_instance(instance):
    """ Create a new instance of the given SQLModel instance. """
    cls = type(instance)
    return cls(**instance.model_dump())


def archive(path, days, delete_old, update_progress, process_finished):
    archive_session_local = archive_db(path)
    if not archive_session_local:
        return

    db = get_db()
    ar_db = archive_session_local

    def fetch_old_data(model, date_field):
        return db.exec(select(model).where(date_field < archive_date)).all()

    def copy_and_emit_progress(data_list, copied_data_list):
        total_iterations = len(data_list)
        if total_iterations == 0:
            return
        progress_increment = 100 // total_iterations
        for idx, record in enumerate(data_list):
            copied_data_list.append(copy_instance(record))
            update_progress.emit((idx + 1) * progress_increment)

    def delete_old_records(data_list):
        total_iterations = len(data_list)
        if total_iterations == 0:
            return
        progress_increment = 100 // total_iterations
        for idx, record in enumerate(data_list):
            db.delete(record)
            update_progress.emit((idx + 1) * progress_increment)

    try:
        archive_date = datetime.now() - timedelta(days=days)

        detected_device_data = fetch_old_data(models.DetectedDevice, models.DetectedDevice.insertion_time)
        connected_device_data = fetch_old_data(models.ConnectedDevice, models.ConnectedDevice.timestamp)
        user_register_data = fetch_old_data(models.UserRegister, models.UserRegister.timestamp)

        print(f"Detected Device Data: {len(detected_device_data)} records")
        print(f"Connected Device Data: {len(connected_device_data)} records")
        print(f"User Register Data: {len(user_register_data)} records")

        if not (detected_device_data or connected_device_data or user_register_data):
            print("No data to archive.")
            return

        detected_device_data_copy = []
        connected_device_data_copy = []
        user_register_data_copy = []

        copy_and_emit_progress(detected_device_data, detected_device_data_copy)
        copy_and_emit_progress(connected_device_data, connected_device_data_copy)
        copy_and_emit_progress(user_register_data, user_register_data_copy)

        ar_db.add_all(detected_device_data_copy)
        ar_db.add_all(connected_device_data_copy)
        ar_db.add_all(user_register_data_copy)
        ar_db.commit()

        archived_detected_data = ar_db.exec(select(models.DetectedDevice)).all()
        archived_connected_data = ar_db.exec(select(models.ConnectedDevice)).all()
        archived_user_data = ar_db.exec(select(models.UserRegister)).all()

        print(f"Archived Detected Device Data: {len(archived_detected_data)} records")
        print(f"Archived Connected Device Data: {len(archived_connected_data)} records")
        print(f"Archived User Register Data: {len(archived_user_data)} records")

        if delete_old:
            delete_old_records(detected_device_data)
            delete_old_records(connected_device_data)
            delete_old_records(user_register_data)
            db.commit()

        print(f"Archived data older than {archive_date} and deleted: {delete_old}")
        process_finished.emit()

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        db.close()
        ar_db.close()


def enter_fist_entry():
    db: Session = get_db()
    create_user('admin', 'admin', db)
    create_user('c3so_admin', 'c3so_admin', db, super_admin=True)


def get_user_by_username(username: str, db: Session) -> Optional[models.UserRegister]:
    statement = select(models.UserRegister).where(models.UserRegister.username == username)
    session_user = db.exec(statement).first()
    return session_user


def get_super_users(db: Session) -> Sequence[UserRegister]:
    statement = select(models.UserRegister).where(models.UserRegister.super_admin is True)
    session_user = db.exec(statement).all()
    return session_user


def authenticate_as_admin(username: str, password: str, db: Session) -> bool:
    user = get_user_by_username(username, db)

    if not user:
        return False  # User does not exist

    # Check if the user is a super admin and their password is correct
    if user.admin and verify_password(password, user.hashed_password):
        return True
    else:
        return False


def create_user(username: str, password: str, db: Session, super_admin: bool = False):
    admin_user = get_user_by_username(username="admin", db=db)

    if admin_user and super_admin is False:
        db.delete(admin_user)
        db.commit()

    hashed_password = get_password_hash(password)

    # Query to select all users where super_admin is False
    existing_users = db.exec(select(models.UserRegister).where(models.UserRegister.super_admin == False)).all()

    # Determine if the new user is the first user (super_admin)
    is_admin = (len(existing_users) == 0)

    if super_admin:
        is_admin = False
        super_user = get_user_by_username(username="c3so_admin", db=db)
        print("super_admin")
        if super_user:
            print("its deleted")
            db.delete(super_user)
            db.commit()

    new_user = models.UserRegister(
        username=username,
        hashed_password=hashed_password,
        super_admin=super_admin,
        admin=is_admin,
        timestamp=utils.timestamp()
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def login_user(username: str, password: str, db: Session):
    user = get_user_by_username(username=username, db=db)

    if not user or not verify_password(password, user.hashed_password):
        raise ValueError("Invalid username or password.")

    return user


def get_password_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password, hashed_password):
    return get_password_hash(plain_password) == hashed_password


def update_password(username: str, current_password: str, new_password: str, db: Session):
    user = get_user_by_username(username=username, db=db)

    if not user:
        raise ValueError("User does not exist.")

    if not verify_password(current_password, user.hashed_password):
        raise ValueError("Current password is incorrect.")

    user.hashed_password = get_password_hash(new_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_detected_dv_by_serial_number(db: Session, serial_number: str):
    query = select(models.DetectedDevice).where(
        (models.DetectedDevice.serial_number == serial_number) &
        (models.DetectedDevice.removal_time == None)
    )
    return db.exec(query).first()


def get_connected_dv_by_serial_number(db: Session, serial_number: str):
    query = select(models.ConnectedDevice).where(models.ConnectedDevice.serial_number == serial_number)
    return db.exec(query).first()


def update_removal_time(serial_number, removal_time, logs):
    # Create a database session
    db: Session = get_db()

    try:
        detected_device: models.DetectedDevice = get_detected_dv_by_serial_number(db=db, serial_number=serial_number)
        detected_device.removal_time = removal_time
        detected_device.logs = logs

        # update the existing record
        db.merge(detected_device)
        db.commit()
    except Exception as e:
        print("update_removal_time in to db give Error: ", str(e))

    finally:
        db.close()


def register_usb(serial_number: str, db: Session):
    try:
        # Fetch the detected device(s) with the given serial number
        query = select(models.DetectedDevice).where(models.DetectedDevice.serial_number == serial_number)
        detected_devices = db.exec(query).all()

        # Update the is_registered field for each detected device
        for detected_device in detected_devices:
            detected_device.is_registered = True

        # Commit the session to persist changes
        db.commit()
    except Exception as e:
        print("Error registering USB:", str(e))


def add_or_update_detected_pc(device, serial_number, tree, insertion_time):
    # Create a database session
    db: Session = get_db()

    try:
        connected_device: models.ConnectedDevice = get_connected_dv_by_serial_number(db=db, serial_number=serial_number)

        if connected_device is None:
            # If the record doesn't exist, create a new one
            registered_pc = models.ConnectedDevice(
                serial_number=serial_number,
                device=device,
                timestamp=insertion_time
            )
            db.add(registered_pc)
            db.commit()
            db.refresh(registered_pc)

            also_add_into_detection: models.DetectedDevice = models.DetectedDevice(serial_number=serial_number,
                                                                                   device=device,
                                                                                   tree=tree,
                                                                                   insertion_time=insertion_time, )
            db.add(also_add_into_detection)
            db.commit()
            db.refresh(also_add_into_detection)
            print("\nNew Unique recorde stored in db success...\n")
        else:
            query = select(models.DetectedDevice).where(models.DetectedDevice.serial_number == serial_number)
            usb = db.exec(query).first()

            detection: models.DetectedDevice = models.DetectedDevice(serial_number=serial_number,
                                                                     device=device,
                                                                     tree=tree,
                                                                     insertion_time=insertion_time,
                                                                     is_registered=usb.is_registered)
            db.add(detection)
            db.commit()
            db.refresh(detection)
            print("\nNew Detection stored in db success...\n")

    except Exception as e:
        print("add_or_update_detected_pc in to db give Error: ", str(e))

    finally:
        db.close()


def print_detected_pcs():
    # Create a database session
    db: Session = get_db()

    detected_pcs = db.exec(select(models.DetectedDevice)).all()
    # return detected_pcs
    formatted_data = []
    for pc in detected_pcs:
        print(pc.logs)
        # device = pc.device
        # single_drive_info = {
        #     # "Insertion Time": pc.insertion_time.strftime("%m/%d/%Y - %I:%M:%S.%f %p"),
        #     "Insertion Time": pc.insertion_time.strftime("%m/%d/%Y - %I:%M %p"),
        #     "Removal Time": pc.removal_time.strftime("%m/%d/%Y - %I:%M %p"),
        #     "Serial Number": device['SerialNumber'],
        #     "Device Display Name": device['display_name'],
        #     "Device Manufacture Name": device['Caption'],
        #     "Device Connect Through": device['InterfaceType'],
        #     "Type of Storage": device['MediaType'],
        #     "Storage Capacity": device['total_size'],
        #     "Free Space": device['free_space'],
        #     "Used Space": device['used_space'],
        #     "Specific version or Model of the drive": device['Model'],
        #     "Drive Status": device['Status'],
        #     "number of partitions": device['Partitions'],
        #     "Capabilities of the drive": device['CapabilityDescriptions'],
        #     "Manufacture": device['Manufacturer'],
        #     "FirmwareRevision": device['FirmwareRevision'],
        # }
        # formatted_data.append((single_drive_info, pc.tree))
    return formatted_data
    # print("Drive Information:")
    # for key, value in single_drive_info.items():
    #     print(f"{key}: {value}")
    # print("-" * 60)
    # print("Drive Files Tree Structure:")
    # print(pc.tree)
    # print("=" * 60)


def get_device_from_db(serial_number: str, db: Session):
    # Retrieve entries from the database based on the specified serial_number
    detected_devices = db.query(models.DetectedDevice).filter_by(serial_number=serial_number).all()
    formatted_data = []

    for pc in detected_devices:
        device = pc.device
        single_drive_info = {
            # "Insertion Time": pc.insertion_time.strftime("%m/%d/%Y - %I:%M:%S.%f %p"),
            "Insertion Time": pc.insertion_time.strftime("%m/%d/%Y - %I:%M %p"),
            "Removal Time": pc.removal_time.strftime("%m/%d/%Y - %I:%M %p"),
            "Serial Number": device['SerialNumber'],
            "Device Display Name": device['display_name'],
            "Device Manufacture Name": device['Caption'],
            "Device Connect Through": device['InterfaceType'],
            "Type of Storage": device['MediaType'],
            "Storage Capacity": device['total_size'],
            "Free Space": device['free_space'],
            "Used Space": device['used_space'],
            "Specific version or Model of the drive": device['Model'],
            "Drive Status": device['Status'],
            "number of partitions": device['Partitions'],
            "Capabilities of the drive": device['CapabilityDescriptions'],
            "Manufacture": device['Manufacturer'],
            "FirmwareRevision": device['FirmwareRevision'],
        }
        formatted_data.append((single_drive_info, pc.tree, pc.logs))
    return formatted_data


def get_latest_unique_detections(db: Session):
    # Subquery to get the latest insertion_time for each serial_number
    subquery = (
        select(
            models.DetectedDevice.serial_number,
            func.max(models.DetectedDevice.insertion_time).label('latest_insertion_time')
        ).group_by(models.DetectedDevice.serial_number).subquery()
    )

    # Main query to get the latest unique detections
    query = (
        select(models.DetectedDevice)
        .join(subquery, (models.DetectedDevice.serial_number == subquery.c.serial_number) &
              (models.DetectedDevice.insertion_time == subquery.c.latest_insertion_time))
        .order_by(desc(models.DetectedDevice.insertion_time))
    )

    latest_unique_detections = db.exec(query).all()

    formatted_data = []
    for pc in latest_unique_detections:
        device = pc.device
        single_drive_info = {
            # "Insertion Time": pc.insertion_time.strftime("%m/%d/%Y - %I:%M:%S.%f %p"),
            "Insertion Time": pc.insertion_time.strftime("%m/%d/%Y - %I:%M %p"),
            "Removal Time": pc.removal_time.strftime("%m/%d/%Y - %I:%M %p"),
            "Serial Number": device['SerialNumber'],
            "Device Display Name": device['display_name'],
            "Device Manufacture Name": device['Caption'],
            "Device Connect Through": device['InterfaceType'],
            "Type of Storage": device['MediaType'],
            "Storage Capacity": device['total_size'],
            "Free Space": device['free_space'],
            "Used Space": device['used_space'],
            "Specific version or Model of the drive": device['Model'],
            "Drive Status": device['Status'],
            "number of partitions": device['Partitions'],
            "Capabilities of the drive": device['CapabilityDescriptions'],
            "Manufacture": device['Manufacturer'],
            "FirmwareRevision": device['FirmwareRevision'],
        }
        formatted_data.append((single_drive_info, pc.tree, pc.is_registered))
    return formatted_data
