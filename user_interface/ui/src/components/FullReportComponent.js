import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import '../styles/FullReportComponent.css';

function FullReportComponent() {
    const { hash } = useParams(); // URL parameter
    const navigate = useNavigate();

    const [record, setRecord] = useState(null);
    const [error, setError] = useState(null);
    const [reportName, setReportName] = useState('N/A'); // Default to 'N/A'

    // Fetch the report details from the backend
    useEffect(() => {
        fetch(`http://localhost:5000/api/report/${hash}`)
            .then(async (response) => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then((data) => {
                setRecord(data);
                // Extract the file name when the record is set
                if (data?.file_path) {
                    const parts = data.file_path.split(/[/\\]/); // Split by slashes
                    const fileNameWithExtension = parts[parts.length - 1] || 'N/A'; // Extract the file name
                    const fileNameWithoutExtension = fileNameWithExtension.split('.').slice(0, -1).join('.') || fileNameWithExtension; // Remove extension
                    setReportName(fileNameWithoutExtension);
                }
            })
            .catch((err) => setError(`An error occurred: ${err.message}`));
    }, [hash]);

    // Helper function to format lists or fallback to "N/A"
    const formatList = (items) => {
        if (Array.isArray(items)) {
            return items.length > 0 ? items.join(', ') : 'N/A';
        }
        return typeof items === 'string' && items.trim() ? items : 'N/A';
    };

    const formatText = (text) => (text && text !== 'none_found' ? text : 'N/A');

    // Conditional rendering for error or loading states
    if (error) {
        return (
            <div className="full-report-container">
                <p>Error: {error}</p>
                <button onClick={() => navigate(-1)}>Go Back</button>
            </div>
        );
    }

    if (!record) {
        return (
            <div className="full-report-container">
                <p>Loading full report...</p>
            </div>
        );
    }

    return (
        <div className="full-report-container">
            <button className="back-button" onClick={() => navigate(-1)}>
                Go Back
            </button>

            <h2>{reportName} Details</h2>

            <div className="form-style">
                <div className="form-group">
                    <label>File Hash:</label>
                    <div className="form-value">{formatText(record.SHA256_hash)}</div>
                </div>
                <div className="form-group">
                    <label>Classification:</label>
                    <div className="form-value">{formatText(record.highest_classification)}</div>
                </div>
                <div className="form-group">
                    <label>Caveats:</label>
                    <div className="form-value">{formatText(record.caveats)}</div>
                </div>
                <div className="form-group">
                    <label>Report Name:</label>
                    <div className="form-value">{reportName}</div>
                </div>
                <div className="form-group">
                    <label>Locations:</label>
                    <div className="form-value">{formatList(record.locations)}</div>
                </div>
                <div className="form-group">
                    <label>Timeframes:</label>
                    <div className="form-value">{formatList(record.timeframes)}</div>
                </div>
                <div className="form-group">
                    <label>Subjects:</label>
                    <div className="form-value">{formatList(record.subjects?.split('|'))}</div>
                </div>
                <div className="form-group">
                    <label>Topics:</label>
                    <div className="form-value">{formatList(record.topics?.split('|'))}</div>
                </div>
                <div className="form-group">
                    <label>Keywords:</label>
                    <div className="form-value">{formatList(record.keywords?.split(','))}</div>
                </div>
                <div className="form-group">
                    <label>MGRS:</label>
                    <div className="form-value">{formatList(record.MGRS)}</div>
                </div>
                <div className="form-group">
                    <label>Processed Time:</label>
                    <div className="form-value">
                        {record.processed_time
                            ? new Date(record.processed_time).toLocaleString()
                            : 'N/A'}
                    </div>
                </div>
            </div>

            {/* Images Section */}
            {record.images && Array.isArray(record.images) && record.images.length > 0 && (
                <div className="form-section">
                    <h3>Images</h3>
                    <div className="images-grid">
                        {record.images.map((imgData, i) => (
                            <img
                                key={i}
                                src={`data:image/jpeg;base64,${imgData}`}
                                alt={`Report image ${i}`}
                                className="report-image"
                            />
                        ))}
                    </div>
                </div>
            )}

            {/* Full Text Section */}
            <div className="form-section">
                <h3>Full Text</h3>
                <div className="form-value full-text">{formatText(record.full_text)}</div>
            </div>
        </div>
    );
}

export default FullReportComponent;
