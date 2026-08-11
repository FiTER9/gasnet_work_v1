# 天然气管网智能安全监测与仿真平台 V1.0

面向天然气输配安全生产的可运行软著项目。平台包含用户登录、管网建模、三支路动态仿真、实时监测、AI 风险分析、报警闭环、历史查询以及 PID/DRL 指标对比。

## 快速启动

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python -m uvicorn app.main:app --reload
```

若需开展随机森林、SVM 或 LSTM 离线训练，再执行 `pip install -r requirements-ai.txt`；核心演示无需这些大型依赖。

浏览器访问 `http://127.0.0.1:8000`，演示账号：`admin / Admin@123`。API 文档：`/docs`。

默认使用 SQLite 和内置动态仿真器，无需 MATLAB/MySQL 即可演示。生产环境将 `DATABASE_URL` 改为 `mysql+pymysql://user:password@host/gasnet`。真实 Simulink 接入方式见 `docs/05-Simulink接口方案.md`。

## 测试

```powershell
python -m pytest tests -q -p no:cacheprovider
```

## 安全提示

本系统为仿真、辅助分析和软件著作权演示平台，不替代经认证的 SIS/ESD、SCADA 或人工处置规程。投产前必须完成模型标定、权限加固、冗余通信与现场验收。
