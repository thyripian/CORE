# CORE - Centralized Operational Reporting Engine

## Overview
CORE (Centralized Operational Reporting Engine) is a data processing and querying tool that interacts with Elasticsearch, Postgres, and SQLite, featuring a React-based UI. Follow the instructions below to set up the environment and run the application. *This code is protected intellectual property*; for details, please see the license file or refer to the license section at the end.

## Prerequisites
Make sure you have the following software installed on your machine:

- Python (version >= 3.8)
- pip (for Python package management)
- Node.js and npm (for the frontend interface)
- Elasticsearch (version 8.x or above)
- PostgreSQL (version >= 12.x)

### Ensure you have the synthetic data if you intend to run the app:
If you have access to the synth data repo, you can download the data from:
https://github.com/thyripian/CORE_synth_data

*If you would like to request access, send an email with your name, affiliation, and justification to thyripian@gmail.com*

## Project Setup
### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd <your-project-directory>
```
### 2. Python Dependencies
First, make sure your Python environment is properly set up. Install all Python dependencies by running:

```bash
pip install -r requirements.txt
```
*Note: The requirements.txt file is still in development. It may not include all requirements at present.*

### 3. Configuration Setup
You need to adjust two configuration files to match your local environment.

#### config/sys_config.json
This file sets some global configurations for logging, NLP models, and paths. With the testing flag set to ```False``` it will only run through the Elasticsearch logic flow, unless data was stored to the fallback CSV during processing.

Example:

```json
{
    "logging": {
        "log_directory": "./logs"
    },
    "nlp": {
        "model": "en_core_web_sm"
    },
    "keywords": {
        "default_path": "./utilities/default_keywords"
    },
    "output": {
        "fallback_csv": "~/Downloads/CORE_fallback_test.csv"
    },
    "testing_mode": {
        "_comment": "Change testing_flag to true to test all storage options.",
        "testing_flag": false
    }
}
```
Adjust the paths as necessary based on where you want log files or CSV outputs stored.

#### config/settings.json
This file sets up connections to the databases and other services. You'll need to change the following fields based on your local setup (example for Windows):

```json
{
    "directory": "C:\\path\\to\\your\\data",
    "user_config": {
        "postgres": {
            "minconn": 1,
            "maxconn": 10,
            "user": "your_postgres_user",
            "password": "your_postgres_password",
            "host": "localhost",
            "port": "5432",
            "database": "your_database_name"
        },
        "elasticsearch": {
            "hosts": ["https://localhost:9200"],
            "basic_auth": {
                "user": "elastic",
                "password": "your_elastic_password"
            },
            "verify_certs": true,
            "ca_certs": "path/to/your/ca.crt",
            "index": "your_index_name"
        },
        "sqlite": {
            "sqlite_directory": "path/to/your/sqlite/directory"
        },
        "keywords": {
            "keyword_dir": "path/to/your/keywords"
        },
        "logging": {
            "log_directory": "../logs"
        }
    }
}
```
Update this file to reflect your Postgres, Elasticsearch, and SQLite paths, credentials, and other configurations.

### 4. Setting Up the Frontend (React App)
Navigate to the UI folder:

```bash
cd CORE/user_interface/ui
```
Run the following command to install all the required npm packages listed in package-lock.json:

```bash
npm install
```
To start the React frontend:

```bash
npm start
```
This will start the React application, which can be accessed in your browser (usually at http://localhost:3000). It will also initialize all three backend APIs, sequentially. Check the terminal output or log file for status.

##  Running the Application
- Start your backend services (Elasticsearch, Postgres, etc.).
- Open the React frontend in your browser and wait for the application to initialize.
- Begin interacting with the application.

## Directory Structure
- **config/:** Contains ```sys_config.json``` and ```settings.json``` to be customized for your environment.
- **core/:** Contains core logic for initializing and testing the central backend functionality. Primary entry point for backend services.
- **data_extraction/:** Contains the logic for extracting data from files.
- **data_processing/:** Contains the logic for processing the files and the extracted data.
- **database_operations/:** Contains logic for managing and structuring database classes and interactions.
- **file_handling/:** Contains logic for I/O operations.
- **initialization/:** Contains logic for initialization of the backend, including configurations and logging.
- **logs/:** Stores logs generated by the application.
- **search_functionality/:** Contains the logic for querying Elasticsearch. Primary entry point for search interface.
- **tests/:** Contains unit tests, subset of synthetic data for testing, and development logging script for tracing logic flow.
- **update_functionality/:** Contains logic for initiating the processing logic and checking for new data. Primary entry point for update interface.
- **user_interface/ui/:** Contains the React frontend.
- **utilities/:** Includes helper modules for logging, configurations, and data management.

## Future Changes / Future Developments
- **API Expansion:** Expanding API functionality for advanced querying and data manipulation.
- **User Roles and Permissions:** Introducing user roles for different access levels within the frontend.
- **Updating Search Results:** Updating mapping logic, refining results list, and refining individual result-specific viewing pages.
- **Expanding Map Results:** Expanding map results to show images extracted from files at specific locations.
- **Building out Update History Page:** Tracking all prior updates within the user interface.
- **Codebase Cleanup:** There are legacy components and outdated code from past versions of the application that will be gradually removed as development progresses.
- **Repair Unit Tests:** Following switch to current package structure, unit tests broke. They will need to be restructured and rewritten.

## License
This software and its source code are the intellectual property of Kevan White (thyripian). No part of this codebase may be reproduced, distributed, or transmitted in any form or by any means, including photocopying, recording, or other electronic or mechanical methods, without the prior written permission of the owner.

Unauthorized use, modification, or distribution of this software is strictly prohibited and may result in legal action.
