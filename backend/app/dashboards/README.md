# Streamlit Dashboards Module

This module provides integration between Streamlit dashboards and the FastAPI backend.

## Usage

Dashboards are automatically mounted when the FastAPI application starts. The demo dashboard is available at:

- **FastAPI endpoint**: `http://localhost:8000/dashboard`
- **Direct Streamlit**: `http://localhost:8501`

## Adding New Dashboards

1. Create a new Streamlit dashboard file in the `dashboards/` directory
2. Add the dashboard to `main.py` using `mount_streamlit_app()`:

```python
mount_streamlit_app(
    app=app,
    dashboard_path="app/dashboards/your_dashboard.py",
    mount_path="/your-dashboard-route",
    port=8502  # Use a different port for each dashboard
)
```

## Demo Dashboard

The demo dashboard (`demo_dashboard.py`) demonstrates:
- Data visualization with charts and graphs
- Interactive widgets and controls
- Metric displays
- Date range filtering
- Data export functionality

## Architecture

The integration runs Streamlit as a subprocess and embeds it in FastAPI using an iframe. This approach allows:
- Multiple Streamlit dashboards to run on different ports
- FastAPI to continue serving its API endpoints
- Dashboards to maintain their interactive features

## Notes

- Ensure Streamlit is installed: `pip install streamlit`
- Each dashboard runs on a separate port
- For production deployments, consider running Streamlit as a separate service
