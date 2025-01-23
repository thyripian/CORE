import json
import logging
import os
import sys

import requests
from elasticsearch import ConnectionError, Elasticsearch, NotFoundError
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)
from utilities.logging.logging_utilities import init_logging, setup_logging

logfile_response = requests.get("http://localhost:5005/api/logfile")
logfile_response.raise_for_status()
logfile = logfile_response.json().get("logfile_name")
setup_logging(log_filename=logfile, log_directory="../../logs")
logger = logging.getLogger(__name__)

try:
    from database_operations.db_manager import DatabaseManager
    from initialization.init_app import AppInitialization
    from utilities.configurations.configs import AppConfig

    db_flag = True
    config_flag = True
    logger.info(
        "Successfully imported DatabaseManager, AppInitialization, and AppConfig"
    )
except ImportError as e:
    db_flag = False
    config_flag = False
    logger.error(
        f"Error importing DatabaseManager, AppInitialization, or AppConfig: {e}"
    )

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

clin = None
initialized = False

# Fetch configuration from run_app.py
try:
    response = requests.get("http://localhost:5005/api/config")  # Adjust port if needed
    response.raise_for_status()
    elastic_conn_info = response.json()
    logger.info(f"Fetched config: {elastic_conn_info}")
except Exception as e:
    logger.info(f"Failed to connect to run_app API: {str(e)}")
    elastic_conn_info = {}

if elastic_conn_info:
    try:
        hosts = elastic_conn_info.get("hosts")
        logger.info(f"Before type check: TYPE HOSTS: {type(hosts)}")
        logger.info(f"HOSTS TEXT: {hosts}")
        # Check if hosts is indeed a list
        if not isinstance(hosts, list):
            raise ValueError(f"Hosts is not a list: {hosts}")
        clin = Elasticsearch(
            hosts,
            basic_auth=(
                elastic_conn_info.get("basic_auth", {}).get("user"),
                elastic_conn_info.get("basic_auth", {}).get("password"),
            ),
            verify_certs=elastic_conn_info.get("verify_certs"),
            ca_certs=elastic_conn_info.get("ca_certs"),
            max_retries=1,
            retry_on_timeout=True,
        )
        if clin.ping():
            initialized = True
        else:
            logger.error("Elasticsearch cluster not reachable")
    except Exception as e:
        logger.error(f"Error initializing Elasticsearch client: {e}")
        initialized = False


def query_elasticsearch(query):
    """
    Function to query Elasticsearch for the provided search term.

    Args:
        query (str): The search query string.

    Returns:
        tuple: A tuple containing a list of records and the total number of hits.
    """
    if not clin:
        logger.info("Elasticsearch client is not available")
        return [], 0
    try:
        index = elastic_conn_info.get("index")
        response = clin.search(
            index=index, query={"match": {"full_text": query}}, size=100
        )
        records = []
        total_hits = response["hits"]["total"]["value"]
        if response["hits"]["hits"]:
            for doc in response["hits"]["hits"]:
                mgrs = doc["_source"].get("MGRS", "[]")
                if isinstance(mgrs, str):
                    mgrs = json.loads(mgrs)
                record = {
                    "SHA256_hash": doc["_id"],
                    "file_path": doc["_source"]["file_path"].split("\\")[-1],
                    "processed_time": doc["_source"]["processed_time"],
                    "MGRS": mgrs,
                    "highest_classification": doc["_source"].get(
                        "highest_classification", ""
                    ),
                }
                records.append(record)
        return records, total_hits
    except ConnectionError as e:
        logger.error(f"ConnectionError querying Elasticsearch: {e}")
        return [], 0
    except NotFoundError as e:
        logger.error(f"Index not found in Elasticsearch: {e}")
        return [], 0
    except Exception as e:
        logger.error(f"Error querying Elasticsearch: {e}")
        return [], 0


def retrieve_report(SHA256_hash: str):
    """
    Fetch a single document from Elasticsearch by file_hash (used as _id).

    Args:
        file_hash (str): The unique identifier for the file in ES.

    Returns:
        dict: The full document's fields, or an empty dict if not found.
    """
    if not clin:
        logger.info("Elasticsearch client is not available")
        return {}
    try:
        index = elastic_conn_info.get("index")

        # If you used file_hash as the ES _id, you can just call .get
        doc = clin.get(index=index, id=SHA256_hash)

        # doc["_source"] has all the fields
        source = doc["_source"]

        # Build your final record. You can either return everything directly,
        # or sanitize fields / transform as needed.
        record = {
            "SHA256_hash": doc["_id"],
            "highest_classification": source.get("highest_classification", ""),
            "caveats": source.get("caveats", []),
            "file_path": source.get("file_path"),
            "locations": source.get("locations", []),
            "timeframes": source.get("timeframes", []),
            "subjects": source.get("subjects", ""),
            "topics": source.get("topics", ""),
            "keywords": source.get("keywords", ""),
            "MGRS": source.get("MGRS", []),
            "images": source.get("images", []),  # base64 or however stored
            "full_text": source.get("full_text", ""),
            "processed_time": source.get("processed_time", ""),
        }
        return record
    except NotFoundError:
        logger.error(f"Document with file_hash={SHA256_hash} not found.")
        return {}
    except ConnectionError as e:
        logger.error(f"ConnectionError retrieving document from Elasticsearch: {e}")
        return {}
    except Exception as e:
        logger.error(f"Error retrieving document: {e}")
        return {}


@app.get("/api/search")
async def search(query: str):
    """
    RESTful endpoint to perform a search query in Elasticsearch.

    Args:
        query (str): The search query string.

    Returns:
        JSONResponse: A JSON response containing the search results or an error message.
    """
    if not query:
        raise HTTPException(status_code=400, detail="No query provided")

    # Perform the search query
    try:
        records, total_hits = query_elasticsearch(query)
        if not records:
            raise HTTPException(status_code=404, detail="No documents found")
        return JSONResponse(
            status_code=200, content={"total_hits": total_hits, "records": records}
        )
    except Exception as e:
        logger.error(f"Error handling search request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/report/{SHA256_hash}")
async def get_full_report(SHA256_hash: str):
    """
    RESTful endpoint to return report details when clicked in the search results.

    """
    if not SHA256_hash:
        raise HTTPException(status_code=400, detail="Unable to find hash.")

    try:
        record = retrieve_report(SHA256_hash)
        if not record:
            raise HTTPException(status_code=404, detail="Document not found")
        return JSONResponse(status_code=200, content=record)
    except Exception as e:
        logger.error(f"Error handling get_full_report request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/status")
async def search_init_status():
    """
    RESTful endpoint to check the readiness status of the application.

    Returns:
        JSONResponse: A JSON response indicating whether the application is ready or still initializing.
    """
    global initialized
    if initialized:
        return JSONResponse(status_code=200, content={"status": "ready"})
    else:
        return JSONResponse(status_code=503, content={"status": "initializing"})


@app.exception_handler(Exception)
async def handle_exception(request: Request, exc: Exception):
    """
    RESTful global exception handler.

    Args:
        request (Request): The incoming request that caused the exception.
        exc (Exception): The exception that was raised.

    Returns:
        JSONResponse: A JSON response with the error details.
    """
    response = {"error": str(exc)}
    return JSONResponse(status_code=500, content=response)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="info")
