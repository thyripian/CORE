import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import LeafletMapComponent from './LeafletMapComponent';
import '../styles/SearchResultsComponent.css';

function SearchResultsComponent() {
  const location = useLocation();
  const query = location.state?.query || '';
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState('list'); // 'list' or 'map'

  useEffect(() => {
    if (query) {
      setLoading(true);
      fetch(`http://localhost:5000/search?query=${encodeURIComponent(query)}`)
        .then(async response => {
          console.log('Raw response:', response); // Log the raw response
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          const data = await response.json();
          console.log('Parsed data:', data); // Log the parsed data
          setResults(data.records);
          setLoading(false);
        })
        .catch(err => {
          setError(err);
          setLoading(false);
        });
    }
  }, [query]);

  const center = { lat: 37.7749, lng: -122.4194 };
  const markers = results
    .filter(result => result.lat && result.lng)
    .map(result => ({ lat: result.lat, lng: result.lng, name: result.name }));

  return (
    <div className="results-container">
      <div className="search-box-wrapper">
        <div className="search-box">
          <input
            type="text"
            value={query}
            readOnly
            className="search-input"
            placeholder="Search..."
          />
          <button className="search-button">Search</button>
        </div>
        <div className="view-toggle">
          <button
            className={`view-button ${viewMode === 'list' ? 'active' : ''}`}
            onClick={() => setViewMode('list')}
          >
            List View
          </button>
          <button
            className={`view-button ${viewMode === 'map' ? 'active' : ''}`}
            onClick={() => setViewMode('map')}
          >
            Map View
          </button>
        </div>
      </div>
      {loading && <p>Loading...</p>}
      {error && <p>Error: {error.message}</p>}
      <div className="search-results">
        {viewMode === 'list' ? (
          results.length > 0 ? (
            <ul className="results-content">
              {results.map((result, index) => (
                <li key={index}>
                <p>File: {result.file_path}</p>
                <p>Processed Time: {result.processed_time}</p>
                <p>MGRS: {result.MGRS}</p>
              </li>
              ))}
            </ul>
          ) : (
            !loading && <p>No results found</p>
          )
        ) : (
          <LeafletMapComponent center={center} markers={markers} />
        )}
      </div>
    </div>
  );
}

export default SearchResultsComponent;
