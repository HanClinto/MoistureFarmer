# Run tests without PydanticDeprecatedSince20 warnings
export PYTHONWARNINGS="ignore::PydanticDeprecatedSince20"
# Run all tests except for test_simulation_droid
python -m pytest -rP tests/ --ignore tests/test_simulation_droid.py
# NOTE: To run without output print spam, use:
# python -m pytest tests/
# Run only test_gx1_vaporator_full_tank
# python -m pytest -rP tests/test_simulation_vaporators_simple.py::test_gx1_vaporator_full_tank

# Run only power recharge tests
# python -m pytest -rP tests/test_recharging.py::test_recharge_vaporator

# python -m pytest -rP tests/test_simulation_droid.py::test_droid_agent_behavior

# Run only the tests within tests/test_recharging.py
# python -m pytest -rP tests/test_recharging.py