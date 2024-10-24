import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

flag = None
logger = logging.getLogger(__name__)

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)
print(root_dir)

# isort: off
from core import generic
from utilities.configurations.database_config import DatabaseConfig
from initialization.init_app import AppInitialization

# isort: on


@asynccontextmanager
async def lifespan(app):
    global flag
    try:
        if flag is None:
            flag = False
            generic.initialize_backend()  # Run initialization logic
            flag = True
        yield
    except Exception as e:
        flag = False
        logger.error(f"Error initializing application logic: {str(e)}")
        yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/initialize")
async def initialize_route():
    global flag
    if flag:
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Application is already initialized",
            },
        )  # Skip re-initialization

    try:
        generic.initialize_backend()
        flag = True
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Application initialized successfully",
            },
        )
    except Exception as e:
        flag = False
        raise HTTPException(
            status_code=500, detail={"status": "error", "message": str(e)}
        )


@app.get("/api/status")
async def get_status():
    global flag
    if flag is None:
        return JSONResponse(status_code=503, content={"status": "initializing"})
    elif flag:
        return JSONResponse(status_code=200, content={"status": "ready"})
    else:
        return JSONResponse(
            status_code=500, content={"status": "Initialization failed"}
        )


@app.get("/api/config")
async def get_config():
    try:
        if AppInitialization.initialized:
            logger.info(
                f"Returning elastic_conn_data: {DatabaseConfig.elastic_conn_data}"
            )
            return JSONResponse(
                status_code=200, content=DatabaseConfig.elastic_conn_data
            )
        else:
            logger.error("Configuration not initialized")
            raise HTTPException(status_code=500, detail="Configuration not initialized")
    except Exception as e:
        logger.error(f"Error in /api/config: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error retrieving configuration: {str(e)}"
        )


@app.get("/api/settings")
async def get_settings():
    try:
        if AppInitialization.initialized:
            logger.info(
                f"Returning settings from backend: {AppInitialization.settings}"
            )
            return JSONResponse(status_code=200, content=AppInitialization.settings)
        else:
            logger.error("Backend not initialized.")
            raise HTTPException(status_code=500, detail="Backend not initialized")
    except Exception as e:
        logger.error(f"Unable to retrieve settings from backend: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Unable to retrieve settings from backend: {str(e)}",
        )


@app.get("/api/logfile")
async def get_logfile():
    try:
        if AppInitialization.initialized:
            logger.info(
                f"Returning logfile name from backend: {AppInitialization.logfile}"
            )
            return JSONResponse(
                status_code=200, content={"logfile_name": AppInitialization.logfile}
            )
        else:
            logger.error("Backend not initialized.")
            raise HTTPException(status_code=500, detail="Backend not initialized")
    except Exception as e:
        logger.error("Unable to retrieve logfile name from backend.")
        raise HTTPException(
            status_code=500, detail=f"Unable to retrieve logfile name: {str(e)}"
        )


@app.get("/api/availabilities")
async def get_availabilities():
    try:
        if AppInitialization.initialized:
            availabilities = {
                "available": AppInitialization.availability,
                "connects": AppInitialization.connection_status,
            }
            logger.info(f"Returning availability data from backend: {availabilities}")
            return JSONResponse(status_code=200, content=availabilities)
        else:
            logger.error("Backend not initialized.")
            raise HTTPException(status_code=500, detail="Backend not initialized")
    except Exception as e:
        logger.error("Unable to retrieve availabilities from backend.")
        raise HTTPException(
            status_code=500, detail=f"Unable to retrieve availabilities: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5005, log_level="info")
