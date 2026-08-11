from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(100), default="管理员")
    role: Mapped[str] = mapped_column(String(20), default="admin")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class NetworkModel(Base):
    __tablename__ = "network_models"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    diameter: Mapped[float] = mapped_column(Float)
    length: Mapped[float] = mapped_column(Float)
    inlet_pressure: Mapped[float] = mapped_column(Float)
    nominal_flow: Mapped[float] = mapped_column(Float)
    valve_count: Mapped[int] = mapped_column(Integer, default=3)
    valve_config: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


class GasData(Base):
    __tablename__ = "gas_data"
    id: Mapped[int] = mapped_column(primary_key=True)
    time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, index=True)
    simulation_id: Mapped[str] = mapped_column(String(36), index=True)
    branch: Mapped[int] = mapped_column(Integer)
    pressure: Mapped[float] = mapped_column(Float)
    flow: Mapped[float] = mapped_column(Float)
    valve: Mapped[float] = mapped_column(Float)
    risk_level: Mapped[int] = mapped_column(Integer, default=0)


class Alarm(Base):
    __tablename__ = "alarm"
    id: Mapped[int] = mapped_column(primary_key=True)
    time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, index=True)
    device: Mapped[str] = mapped_column(String(100))
    type: Mapped[str] = mapped_column(String(50))
    level: Mapped[int] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="未处理")
    # 不使用 PEP 604 可选注解，以兼容 Python 3.14 + SQLAlchemy 2.0.36；
    # 数据库可空性由 nullable=True 明确定义。
    handled_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    handled_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)


class ControlResult(Base):
    __tablename__ = "control_results"
    id: Mapped[int] = mapped_column(primary_key=True)
    time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    controller: Mapped[str] = mapped_column(String(20))
    pressure_error: Mapped[float] = mapped_column(Float)
    flow_error: Mapped[float] = mapped_column(Float)
    valve_actions: Mapped[int] = mapped_column(Integer)
    settling_time: Mapped[float] = mapped_column(Float)
