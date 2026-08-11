from dataclasses import dataclass


@dataclass
class RiskResult:
    level: int
    risk_type: str
    score: float
    description: str


class HybridRiskModel:
    """可解释安全边界 + AI 异常分数；边界规则始终拥有安全否决权。"""

    def predict(self, pressure: float, flow: float, valve: float) -> RiskResult:
        p_dev = abs(pressure - 4.0) / 4.0
        q_expected = max(5.0, valve * 0.42)
        q_dev = abs(flow - q_expected) / q_expected
        coupling = abs(flow / max(valve, 1) - 0.42) / 0.42
        score = min(1.0, 0.52 * p_dev + 0.33 * q_dev + 0.15 * coupling)
        if pressure < 2.7 or pressure > 5.5:
            return RiskResult(2, "压力异常", max(score, .85), f"压力 {pressure:.2f} MPa 超出危险边界")
        if flow < 4 or flow > 48:
            return RiskResult(2, "流量异常", max(score, .8), f"流量 {flow:.2f} 超出危险边界")
        if valve < 2 or valve > 98:
            return RiskResult(1, "阀门异常", max(score, .55), f"阀门开度 {valve:.1f}% 接近机械限位")
        if score >= .45 or pressure < 3.2 or pressure > 4.8:
            return RiskResult(1, "综合异常", score, "多参数耦合偏离正常运行分布")
        return RiskResult(0, "正常", score, "运行参数处于安全区间")


risk_model = HybridRiskModel()

