# models.py
from sqlmodel import SQLModel, Field, JSON, Column, Text
from datetime import datetime


class ConnectedDevice(SQLModel, table=True):
    __tablename__ = 'connected_devices'

    serial_number: str = Field(primary_key=True, unique=True)
    device: dict = Field(sa_column=Column(JSON))
    timestamp: datetime = Field(nullable=False)


class DetectedDevice(SQLModel, table=True):
    __tablename__ = 'detected_devices'

    id: int = Field(primary_key=True)
    serial_number: str = Field()
    device: dict = Field(sa_column=Column(JSON))
    tree: str = Field(Text)
    insertion_time: datetime = Field(nullable=True)
    removal_time: datetime = Field(nullable=True)
    is_registered: bool = Field(nullable=True)
    logs: str = Field(sa_column=Column(Text, nullable=True))


class UserRegister(SQLModel, table=True):
    __tablename__ = 'register_user'

    id: int = Field(primary_key=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str
    super_admin: bool = False
    admin: bool = False
    timestamp: datetime = Field(nullable=False)
