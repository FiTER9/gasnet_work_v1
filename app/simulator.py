import asyncio
import math
import random
import uuid
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SimulationState:
    simulation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: str = "stopped"
    tick: int = 0
    valves: list[float] = field(default_factory=lambda: [62.0, 56.0, 49.0])
    pressures: list[float] = field(default_factory=lambda: [4.1, 3.9, 3.8])
    flows: list[float] = field(default_factory=lambda: [26.0, 23.0, 20.0])


class BuiltinSimulator:
    def __init__(self):
        self.state = SimulationState()
        self.lock = asyncio.Lock()

    async def command(self, action: str):
        async with self.lock:
            if action == "start":
                self.state = SimulationState(status="running")
            elif action == "pause" and self.state.status == "running":
                self.state.status = "paused"
            elif action == "resume" and self.state.status == "paused":
                self.state.status = "running"
            elif action == "stop":
                self.state.status = "stopped"
            return self.snapshot()

    async def step(self):
        async with self.lock:
            s = self.state
            if s.status == "running":
                s.tick += 1
                inlet = 4.35 + .12 * math.sin(s.tick / 18)
                for i in range(3):
                    target_u = [62, 56, 49][i] + 5 * math.sin(s.tick / (22 + i * 5) + i)
                    s.valves[i] += .12 * (target_u - s.valves[i])
                    target_q = .42 * s.valves[i] * (inlet / 4.2) ** .5
                    s.flows[i] += .18 * (target_q - s.flows[i]) + random.gauss(0, .05)
                    target_p = inlet - .010 * s.flows[i] - .03 * i
                    s.pressures[i] += .15 * (target_p - s.pressures[i]) + random.gauss(0, .006)
            return self.snapshot()

    def snapshot(self):
        s = self.state
        return {"simulation_id": s.simulation_id, "status": s.status, "tick": s.tick,
                "time": datetime.now().isoformat(timespec="seconds"),
                "P": [round(x, 3) for x in s.pressures], "Q": [round(x, 3) for x in s.flows],
                "U": [round(x, 2) for x in s.valves]}


simulator = BuiltinSimulator()
