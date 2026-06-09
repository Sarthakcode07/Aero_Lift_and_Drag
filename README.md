# Aero Lift and Drag Dashboard

A Streamlit-based aerodynamic dashboard for visualizing lift and drag, simulating takeoff performance, and asking an AI aero expert follow-up questions.

## Features

- Real-time lift and drag calculation from user-controlled inputs
- Aircraft profile presets: Cessna 172, Boeing 737-800, F-16 Falcon
- Fluid dynamics diagnostics panel with Reynolds number and Mach number
- Compressibility warning for Mach > 0.3 and supersonic accent styling for Mach > 1.0
- Takeoff performance simulator with runway length, thrust, payload, and rolling friction
- Animated velocity plot and success/failure reporting for lift-off before runway end
- Local Ollama AI integration for follow-up aerospace questions

## Project Structure

- `run_app.py` - entrypoint for launching the Streamlit app
- `requirements.txt` - Python dependencies
- `aero_dashboard/`
  - `app_main.py` - Streamlit UI and main dashboard logic
  - `visuals.py` - plotting helpers, UI cards, and takeoff simulation logic
  - `agent.py` - Ollama integration and AI prompt management

## Installation

This project is designed to run in a Python virtual environment.

```bash
cd "c:/Sarthak_Code/Sarthak Aero"
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

## Running the App

Start the aerodynamic dashboard with either of these:

```bash
python app.py
```

or

```bash
python run_app.py
```

Start the professional email agent website with:

```bash
streamlit run email_agent_app.py
```

Then open the displayed Streamlit URL in your browser.

Note: The app now includes a home page where users can sign in or continue as a guest before accessing the dashboard.

## Ollama AI Agent

The dashboard includes an AI Aero Expert panel powered by a local Ollama instance.

### Requirements

- `ollama` installed locally
- Ollama service running on `http://localhost:11434`
- At least one model pulled locally, e.g. `mistral`

### Recommended commands

```bash
ollama serve
ollama pull mistral
```

If Ollama is unavailable, the app will warn you and continue to display the simulation controls.

## Usage

1. Choose an aircraft profile from the top dropdown.
2. Adjust velocity, wing area, lift/drag coefficients, and air density.
3. Use the sidebar to enter runway length, payload, thrust, and rolling friction.
4. View diagnostics for Reynolds number and Mach number.
5. Click `Run Takeoff Simulator` to simulate ground roll performance.
6. Ask the AI Aero Expert follow-up questions using the form.

## Notes

- The takeoff simulation uses a simplified physics model with drag, rolling friction, and lift generation.
- The diagnostics panel calculates Reynolds and Mach numbers from the current velocity slider and wing area.
- The AI model selection dropdown lists available Ollama models if the service is running.

## License

This repository is built for personal aerodynamic analysis and demonstration.
