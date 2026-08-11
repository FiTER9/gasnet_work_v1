% Simulink 模型输出规范示例：模型中将 P/Q/U 通过 To Workspace 输出为 timeseries
function data = gasnet_export(modelName, stopTime)
    if nargin < 1, modelName = 'gas_network'; end
    if nargin < 2, stopTime = 60; end
    load_system(modelName);
    out = sim(modelName, 'StopTime', num2str(stopTime), 'ReturnWorkspaceOutputs', 'on');
    data.time = out.P.Time;
    data.P = out.P.Data;
    data.Q = out.Q.Data;
    data.U = out.U.Data;
end

