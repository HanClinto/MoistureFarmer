# MoistureFarmer - Agentic AI Simulation Platform

MoistureFarmer is an experimental sandbox for agentic AI that simulates a moisture farming environment on a desert planet. It features component-based droid management, multi-agent AI systems, and a Windows 98-styled web interface.

**Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.**

## Working Effectively

### Bootstrap, Build, and Test the Repository
- Navigate to the code directory: `cd code`
- Install Python dependencies: `pip install -r requirements.txt` -- takes 15 seconds. NEVER CANCEL.
- Run tests: `bash run_tests.sh` -- takes 3 seconds. **Note:** Some Pydantic model tests currently fail (12 failures, 18 pass) but this is a known issue.
- Alternative test command: `python -m pytest tests/`

### Run the Web Application
- **ALWAYS run the bootstrapping steps first.**
- Start web server: `bash start_webgui.sh` OR `uvicorn webgui.server:app --reload`
- Navigate to: http://127.0.0.1:8000
- Application loads automatically to `/web98/index.html` with Windows 98 styling
- **NEVER CANCEL:** Web server starts in 5-10 seconds. Set timeout to 30+ seconds.

### Alternative GUI (Pygame) - Windows Only
- **DO NOT attempt on Linux/Mac:** `bash pygamegui/run_viewer.sh` -- only works on Windows with specific Python paths
- Use the web GUI instead for cross-platform development

## Validation

### Manual Validation Requirements
After making any changes to the simulation or web interface:

1. **Start the web application** using the steps above
2. **Verify simulation is running:** Check that the "Tick:" counter is incrementing in the main window
4. **Test simulation controls:** Use Pause/Resume button and speed controls (1x, 4x, 10x)
5. **Test world view:** Open World View window and test zoom controls (-/+, Fit, Center)
6. **Verify Windows 98 styling:** Confirm all windows have proper title bars, buttons, and retro styling

### Screenshots for Validation
Take full-page screenshots to document working functionality. The application should show:
- Main Moisture Farmer v0.98 window with menu bar
- World View window with zoom controls
- Desert/sandy background with proper Windows 98 window styling
- Other windows and UI elements as-appropriate for the simulation

## Common Tasks

### Repository Structure
```
code/
├── requirements.txt           # Python dependencies
├── start_webgui.sh           # Web server launcher
├── run_tests.sh              # Test runner script
├── system_config.json        # Configuration
├── webgui/                   # Web-based GUI (main interface)
│   ├── server.py            # FastAPI server
│   ├── web98/               # Windows 98 styled frontend
│   └── resources/           # Static assets
├── pygamegui/               # Alternative pygame GUI (Windows only)
├── simulation/              # Core simulation engine
│   ├── core/               # Core simulation classes
│   ├── equipment/          # Droid and equipment models
│   └── llm/                # LLM integration components
├── scenarios/               # Test scenarios
│   └── example_scenario.json # Default scenario
└── tests/                   # Test suite (pytest)
```

### Key Files and Their Purpose
- `webgui/server.py` - FastAPI backend server
- `simulation/core/` - Core game engine and entity management
- `simulation/equipment/DroidModels.py` - Droid chassis definitions
- `scenarios/example_scenario.json` - Default simulation scenario
- `web98/` - Frontend HTML/CSS/JS with Windows 98 styling

### Dependencies
Python 3.12+ required. Key packages:
- `fastapi` - Web backend framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation (some model rebuild warnings are normal)
- `pytest` - Testing framework
- `aiohttp` - Async HTTP client

### Build Times and Timeouts
- **Dependencies installation:** 15 seconds - Set timeout to 30+ seconds
- **Test suite execution:** 3 seconds - Set timeout to 30+ seconds  
- **Web server startup:** 5-10 seconds - Set timeout to 30+ seconds
- **NEVER CANCEL:** All operations complete quickly, but always allow sufficient time

### Known Issues and Workarounds
- **Pydantic model warnings:** Normal at startup, simulation still functions correctly
- **Test failures:** 12 Pydantic-related test failures are expected, 18 core tests pass
- **Docker builds:** May fail due to SSL/firewall restrictions - use local Python environment instead
- **Pygame GUI:** Only works on Windows - use web GUI for development

### Configuration
- Default scenario: `scenarios/example_scenario.json`
- System config: `system_config.json`
- Web server runs on port 8000 by default
- Simulation includes GonkDroid and GX1 Vaporator by default

### Development Workflow
1. Make code changes in `simulation/` or `webgui/`
2. Run tests: `bash run_tests.sh` (expect some failures, focus on new test results)
3. Start web server: `bash start_webgui.sh`
4. Manually validate using the validation steps above
5. Take screenshots if UI changes were made

### Debugging
- Server logs display in terminal when running `start_webgui.sh`
- Check browser console for frontend JavaScript errors
- Use pytest `-v` flag for verbose test output: `python -m pytest -v tests/`
- Test individual modules: `python -m pytest tests/test_simulation_droid.py`

## Architecture Notes

### Component-Based Design
- Chassis (droids/equipment) hold multiple component slots
- Components add functionality via tool-calling capabilities
- Example: Motivator component adds movement, PowerPack adds energy storage

### Multi-Agent AI Integration
- Designed for LLM-based agent control of droids
- Context management and error handling for agent "reboots"
- Scenario-based challenges for AI benchmarking
- Tool calls are made available to LLM agents via component slots
- Each droid has its own unique set of tool calls and context based on its components and history

### Frontend Technology
- FastAPI backend with Server-Sent Events (SSE) for real-time updates
- HTML/CSS/JS frontend with 98.css for Windows 98 styling
- Canvas-based world rendering with entity management
- Loosely-coupled front-end that is backend agnostic.
- No npm / install required -- simple Javascript and HTML with no frameworks.

### Backend Technology
- Can be run independently of any GUI, allowing for headless operation (such as when benchmarking prompts and LLMs)
- Serves GUIs (optionally) via lightweight FastAPI server

### Game Simulation
- Tick-based simulation engine
- Pausable with speed controls (1x, 4x, 10x)
- Component lifecycle management (on_tick routines)
- Resource management (power, water, durability)

Always test both the simulation engine and web interface after making changes to ensure the complete system remains functional.