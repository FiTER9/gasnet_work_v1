from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ValveConfig(BaseModel):
    min_opening: float = Field(0, ge=0, le=100)
    max_opening: float = Field(100, ge=0, le=100)
    response_speed: float = Field(20, gt=0, le=100)


class NetworkCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    diameter: float = Field(gt=0)
    length: float = Field(gt=0)
    inlet_pressure: float = Field(gt=0)
    nominal_flow: float = Field(gt=0)
    valve_count: int = Field(3, ge=1, le=20)
    valves: list[ValveConfig] = Field(default_factory=lambda: [ValveConfig() for _ in range(3)])


class NetworkOut(NetworkCreate):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class SimulationCommand(BaseModel):
    action: str = Field(pattern="^(start|pause|resume|stop)$")


class AlarmOut(BaseModel):
    id: int
    time: datetime
    device: str
    type: str
    level: int
    description: str
    status: str
    model_config = ConfigDict(from_attributes=True)

