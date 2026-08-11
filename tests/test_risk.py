from app.risk import HybridRiskModel


def test_normal_condition():
    assert HybridRiskModel().predict(4.0, 25.2, 60).level == 0


def test_dangerous_pressure_has_safety_veto():
    result = HybridRiskModel().predict(5.8, 25, 60)
    assert result.level == 2
    assert result.risk_type == "压力异常"


def test_valve_limit_is_warning():
    assert HybridRiskModel().predict(4.0, 1, 1).level >= 1

