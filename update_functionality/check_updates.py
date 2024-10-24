import logging
import os
import sys
import threading

import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Ensure the base directory is in the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utilities.logging.logging_utilities import init_logging  # isort: skip
from utilities.logging.logging_utilities import setup_logging

logfile_response = requests.get("http://localhost:5005/api/logfile")
logfile_response.raise_for_status()
logfile = logfile_response.json().get("logfile_name")
setup_logging(log_filename=logfile, log_directory="../../logs")
logger = logging.getLogger(__name__)

from update_functionality import run_update_process  # isort: skip

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

initialized = False


@app.get("/api/status")
async def status():
    """
    RESTful endpoint for checking the readiness status of the application.
    """
    global initialized
    initialized = True  # Replace with actual readiness checks
    if initialized:
        return JSONResponse(status_code=200, content={"status": "ready"})
    else:
        return JSONResponse(status_code=503, content={"status": "initializing"})


@app.get("/api/progress")
async def get_progress():
    """
    RESTful endpoint to get the current progress of the update process.
    """
    return JSONResponse(status_code=200, content=run_update_process.progress_state)


@app.post("/api/updates/check")
async def check_for_updates():
    """
    RESTful endpoint to initiate the update process.
    """
    logger.info("RECEIVED REQUEST TO START UPDATE PROCESS")

    def run_check_updates():
        try:
            run_update_process.run_process()
        except Exception as e:
            logger.error(f"Exception in update process: {e}", exc_info=True)
            run_update_process.progress_state["message"] = f"Failed: {str(e)}"

    threading.Thread(target=run_check_updates).start()
    return JSONResponse(status_code=200, content={"message": "Processing started"})


@app.exception_handler(Exception)
async def handle_exception(request, exc):
    """
    RESTful global exception handler.
    """
    response = {"error": str(exc)}
    return JSONResponse(status_code=500, content=response)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5001, log_level="info", use_colors=False)
