const axios = require('axios');

const checkStatus = async () => {
    try {
        const response = await axios.get('http://localhost:5005/api/status');
        if (response.data && response.data.status === "ready") {
            console.log("Backend service initialized successfully");
            process.exit(0)
        } else {
            console.log("Waiting for backend service to initialize...");
            setTimeout(checkStatus, 2000); // Retry after 2 seconds
        }
    } catch (error) {
        console.error("Error fetching status, retrying...");
        setTimeout(checkStatus, 2000); // Retry after 2 seconds
    }
};

checkStatus()
