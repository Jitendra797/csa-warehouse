"""
Streamlit integration with FastAPI.
This module provides functionality to serve Streamlit apps within FastAPI.
"""
import atexit
import logging
import subprocess
import threading
import time
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

logger = logging.getLogger(__name__)

# Global dictionary to track Streamlit processes
_streamlit_processes = {}


def cleanup_streamlit_processes():
    """Clean up all Streamlit processes on exit"""
    for process in _streamlit_processes.values():
        if process and process.poll() is None:
            try:
                process.terminate()
                process.wait(timeout=5)
                logger.info("Terminated Streamlit process")
            except subprocess.TimeoutExpired:
                process.kill()
                logger.info("Killed Streamlit process")
            except Exception as e:
                logger.error(f"Error cleaning up Streamlit process: {e}")


# Register cleanup on exit
atexit.register(cleanup_streamlit_processes)


def start_streamlit_server(dashboard_path: str, port: int = 8501) -> subprocess.Popen:
    """
    Start a Streamlit server as a subprocess.

    Args:
        dashboard_path: Path to the Streamlit dashboard script
        port: Port to run Streamlit on

    Returns:
        subprocess.Popen: The Streamlit subprocess
    """
    script_path = Path(dashboard_path).resolve()

    if not script_path.exists():
        raise FileNotFoundError(f"Dashboard file not found: {dashboard_path}")

    # Check if Streamlit is already running on this port
    port_key = f"port_{port}"
    if port_key in _streamlit_processes:
        process = _streamlit_processes[port_key]
        if process.poll() is None:
            logger.info(f"Streamlit already running on port {port}")
            return process

    # Start Streamlit server
    cmd = [
        "streamlit",
        "run",
        str(script_path),
        "--server.port", str(port),
        "--server.headless", "true",
        "--server.enableCORS", "false",
        "--server.enableXsrfProtection", "false",
        "--browser.gatherUsageStats", "false",
        "--server.address", "0.0.0.0",
    ]

    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        _streamlit_processes[port_key] = process

        # Give Streamlit a moment to start
        time.sleep(1)

        # Check if process is still running
        if process.poll() is None:
            logger.info(
                f"Started Streamlit server on port {port} for {dashboard_path}")
        else:
            stdout, stderr = process.communicate()
            error_msg = f"Streamlit process exited with code {process.returncode}"
            if stderr:
                error_msg += f": {stderr.decode()}"
            raise RuntimeError(error_msg)

        return process
    except Exception as e:
        logger.error(f"Failed to start Streamlit server: {e}")
        raise


def mount_streamlit_app(app: FastAPI, dashboard_path: str, mount_path: str = "/dashboard", port: int = 8501):
    """
    Mount a Streamlit app to a FastAPI application.
    Creates an iframe endpoint that embeds the Streamlit app.

    Args:
        app: FastAPI application instance
        dashboard_path: Path to the Streamlit dashboard script
        mount_path: URL path to mount the dashboard in FastAPI
        port: Port to run Streamlit on
    """
    # Convert to absolute path
    script_path = Path(dashboard_path).resolve()

    if not script_path.exists():
        logger.warning(f"Dashboard file not found: {dashboard_path}")
        return app

    # Store the path and port for later use
    app.state.streamlit_dashboard_path = str(script_path)
    app.state.streamlit_mount_path = mount_path
    app.state.streamlit_port = port

    # Add an iframe endpoint
    @app.get(mount_path, response_class=HTMLResponse)
    async def streamlit_dashboard():
        """Serve the Streamlit dashboard via iframe"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Streamlit Dashboard</title>
            <style>
                body, html {{
                    margin: 0;
                    padding: 0;
                    width: 100%;
                    height: 100%;
                }}
                iframe {{
                    width: 100%;
                    height: 100vh;
                    border: none;
                }}
            </style>
        </head>
        <body>
            <iframe src="http://localhost:{port}"></iframe>
        </body>
        </html>
        """
        return html_content

    # Start Streamlit server in a separate thread
    def start_server():
        try:
            start_streamlit_server(str(script_path), port)
        except Exception as e:
            logger.error(f"Error starting Streamlit server: {e}")

    thread = threading.Thread(target=start_server, daemon=True)
    thread.start()

    logger.info(
        f"Mounted Streamlit dashboard at {mount_path} from {dashboard_path} on port {port}")
    return app
