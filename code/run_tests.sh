# Run tests without PydanticDeprecatedSince20 warnings
export PYTHONWARNINGS="ignore::PydanticDeprecatedSince20"
python -m pytest -rP tests/
# NOTE: To run without output print spam, use:
# python -m pytest tests/
# Run only test_gx1_vaporator_full_tank
# python -m pytest -rP tests/test_simulation_vaporators_simple.py::test_gx1_vaporator_full_tank

# python -m pytest -rP tests/test_simulation_droid.py::test_droid_agent_behavior