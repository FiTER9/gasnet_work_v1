import asyncio
from app.simulator import BuiltinSimulator


def test_state_machine_and_outputs():
    async def run():
        sim = BuiltinSimulator()
        assert (await sim.command("start"))["status"] == "running"
        data = await sim.step()
        assert len(data["P"]) == len(data["Q"]) == len(data["U"]) == 3
        assert (await sim.command("pause"))["status"] == "paused"
        assert (await sim.command("stop"))["status"] == "stopped"
    asyncio.run(run())

