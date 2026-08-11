# MATLAB Simulink 接口方案

推荐以 MATLAB Engine for Python 作为在线适配器。Simulink 模型将 `P/Q/U` 分别配置为三列 `timeseries`，数据维度为 `N×3`，统一压力 MPa、流量 Nm³/h、阀位百分比。示例离线导出函数见 `matlab/gasnet_export.m`。

在线控制映射：`start` 调用 `set_param(model,'SimulationCommand','start')`；`pause`、`continue`、`stop` 对应相同命令；采样通过 `SimulationOutput`、SDI 或模型内 UDP/TCP 发布模块读取。Python 适配器应在独立工作线程调用 Engine，避免阻塞 FastAPI 事件循环，并把结果归一为：

```json
{"simulation_id":"uuid","status":"running","time":"ISO-8601","P":[4.1,3.9,3.8],"Q":[26,23,20],"U":[62,56,49]}
```

安装 Engine（在 MATLAB 安装目录的 `extern/engines/python` 执行安装）后，将 `.env` 的 `SIMULATOR_MODE=matlab`、`SIMULINK_MODEL=模型名`。接入时需确认模型输出变量名称、采样周期和许可证条件。生产环境建议 Simulink 与 Web 服务进程隔离，通过消息队列传输，设置心跳、超时、断线重连和最后可信值标识。

