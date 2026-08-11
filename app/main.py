import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from sqlalchemy import desc, select
from sqlalchemy.orm import Session
from .config import settings
from .database import Base, SessionLocal, engine, get_db
from .models import Alarm, ControlResult, GasData, NetworkModel, User
from .risk import risk_model
from .schemas import AlarmOut, NetworkCreate, NetworkOut, SimulationCommand, Token
from .security import create_token, current_user, hash_password, verify_password
from .simulator import simulator


def initialize():
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if not db.scalar(select(User).where(User.username == "admin")):
            db.add(User(username="admin", password_hash=hash_password("Admin@123"), full_name="系统管理员"))
        if not db.scalar(select(NetworkModel)):
            db.add(NetworkModel(name="三支路示范管网", diameter=0.6, length=12.5, inlet_pressure=4.2,
                                nominal_flow=70, valve_count=3,
                                valve_config=[{"min_opening": 0, "max_opening": 100, "response_speed": 20}] * 3))
        if not db.scalar(select(ControlResult)):
            db.add_all([
                ControlResult(controller="PID", pressure_error=.142, flow_error=1.83, valve_actions=48, settling_time=18.2),
                ControlResult(controller="DRL", pressure_error=.086, flow_error=1.12, valve_actions=31, settling_time=11.6),
            ])
        db.commit()


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize()
    yield


app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)
web_dir = Path(__file__).parent.parent / "web"
app.mount("/static", StaticFiles(directory=web_dir), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(web_dir / "index.html")


@app.post("/api/auth/token", response_model=Token, tags=["用户管理"])
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.username == form.username))
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(401, "用户名或密码错误")
    return Token(access_token=create_token(user.username))


@app.get("/api/users/me", tags=["用户管理"])
def me(user: User = Depends(current_user)):
    return {"id": user.id, "username": user.username, "full_name": user.full_name, "role": user.role}


@app.get("/api/models", response_model=list[NetworkOut], tags=["模型管理"])
def models(db: Session = Depends(get_db), _: User = Depends(current_user)):
    rows = db.scalars(select(NetworkModel).order_by(desc(NetworkModel.id))).all()
    return [NetworkOut(id=x.id, name=x.name, diameter=x.diameter, length=x.length,
                       inlet_pressure=x.inlet_pressure, nominal_flow=x.nominal_flow,
                       valve_count=x.valve_count, valves=x.valve_config, created_at=x.created_at) for x in rows]


@app.post("/api/models", response_model=NetworkOut, tags=["模型管理"])
def create_model(data: NetworkCreate, db: Session = Depends(get_db), _: User = Depends(current_user)):
    if len(data.valves) != data.valve_count:
        raise HTTPException(422, "阀门配置数量必须等于 valve_count")
    obj = NetworkModel(name=data.name, diameter=data.diameter, length=data.length,
                       inlet_pressure=data.inlet_pressure, nominal_flow=data.nominal_flow,
                       valve_count=data.valve_count, valve_config=[x.model_dump() for x in data.valves])
    db.add(obj); db.commit(); db.refresh(obj)
    return NetworkOut(id=obj.id, created_at=obj.created_at, **data.model_dump())


@app.post("/api/simulation/command", tags=["仿真运行"])
async def simulation_command(cmd: SimulationCommand, _: User = Depends(current_user)):
    return await simulator.command(cmd.action)


@app.get("/api/simulation/state", tags=["仿真运行"])
async def simulation_state(_: User = Depends(current_user)):
    return await simulator.step()


def persist_snapshot(snapshot: dict):
    risks = []
    with SessionLocal() as db:
        for i, (p, q, u) in enumerate(zip(snapshot["P"], snapshot["Q"], snapshot["U"]), 1):
            risk = risk_model.predict(p, q, u); risks.append(risk)
            db.add(GasData(simulation_id=snapshot["simulation_id"], branch=i, pressure=p, flow=q,
                           valve=u, risk_level=risk.level))
            if risk.level > 0:
                recent = db.scalar(select(Alarm).where(Alarm.device == f"支路{i}", Alarm.status == "未处理")
                                   .order_by(desc(Alarm.id)))
                if not recent:
                    db.add(Alarm(device=f"支路{i}", type=risk.risk_type, level=risk.level,
                                 description=risk.description))
        db.commit()
    snapshot["risks"] = [{"level": r.level, "type": r.risk_type, "score": round(r.score, 3),
                           "description": r.description} for r in risks]
    snapshot["overall_level"] = max(r.level for r in risks)
    return snapshot


@app.websocket("/ws/monitor")
async def monitor(ws: WebSocket):
    token = ws.query_params.get("token", "")
    try:
        from jose import jwt
        jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    except Exception:
        await ws.close(code=1008); return
    await ws.accept()
    try:
        while True:
            snap = await simulator.step()
            await ws.send_json(persist_snapshot(snap) if snap["status"] == "running" else snap)
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass


@app.get("/api/history", tags=["历史数据"])
def history(limit: int = 100, db: Session = Depends(get_db), _: User = Depends(current_user)):
    rows = db.scalars(select(GasData).order_by(desc(GasData.id)).limit(min(limit, 1000))).all()
    return [{"id": x.id, "time": x.time, "branch": x.branch, "pressure": x.pressure,
             "flow": x.flow, "valve": x.valve, "risk_level": x.risk_level} for x in rows]


@app.get("/api/alarms", response_model=list[AlarmOut], tags=["报警管理"])
def alarms(db: Session = Depends(get_db), _: User = Depends(current_user)):
    return db.scalars(select(Alarm).order_by(desc(Alarm.id)).limit(200)).all()


@app.patch("/api/alarms/{alarm_id}/handle", response_model=AlarmOut, tags=["报警管理"])
def handle_alarm(alarm_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    alarm = db.get(Alarm, alarm_id)
    if not alarm: raise HTTPException(404, "报警不存在")
    alarm.status, alarm.handled_by, alarm.handled_at = "已处理", user.id, datetime.now()
    db.commit(); db.refresh(alarm); return alarm


@app.get("/api/analysis/controllers", tags=["结果分析"])
def controller_results(db: Session = Depends(get_db), _: User = Depends(current_user)):
    rows = db.scalars(select(ControlResult).order_by(ControlResult.controller)).all()
    return [{"controller": x.controller, "pressure_error": x.pressure_error, "flow_error": x.flow_error,
             "valve_actions": x.valve_actions, "settling_time": x.settling_time} for x in rows]


@app.get("/api/health", tags=["系统"])
def health():
    return {"status": "ok", "version": "1.0.0", "simulator": settings.simulator_mode}

