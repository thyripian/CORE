import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import LeafletMapComponent from './LeafletMapComponent';
import '../styles/SearchResultsComponent.css';

function SearchResultsComponent() {
  const location = useLocation();
  const initialQuery = location.state?.query || '';
  const [query, setQuery] = useState(initialQuery);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState('list');
  const [currentPage, setCurrentPage] = useState(1); // Pagination state // 'list' or 'map'

  useEffect(() => {
    if (initialQuery) {
      setLoading(true);
      setError(null);  // Clear any previous errors
      fetch(`http://localhost:5000/api/search?query=${encodeURIComponent(initialQuery)}`)
        .then(async response => {
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          const data = await response.json();
          setResults(data.records);
        })
        .catch(err => {
          setError(`An error occurred: ${err.message}`);
        })
        .finally(() => {
          setLoading(false);
        });
    }
  }, [initialQuery]);

  const handleSearch = () => {
    if (query.trim()) {
      setResults([]); // Clear previous results
      setLoading(true);
      setError(null);  // Clear previous errors
      fetch(`http://localhost:5000/api/search?query=${encodeURIComponent(query)}`)
        .then(async response => {
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          const data = await response.json();
          setResults(data.records);
        })
        .catch(err => {
          setError(`An error occurred: ${err.message}`);
        })
        .finally(() => {
          setLoading(false);
        });
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

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
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            className="search-input"
            placeholder="Search..."
          />
          <button onClick={() => { handleSearch(); setCurrentPage(1); }} className="search-button">Search</button>
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
      {error && <p>Error: {error}</p>}
      <div className="search-results">
        {viewMode === 'list' ? (
          results.length > 0 ? (
            <div className="results-list-container">
              <ul className="results-content">
                {results.slice((currentPage - 1) * 10, currentPage * 10).map((result, index) => (
                  <li key={index}>
                    <p>File: {result.file_path}</p>
                    <p>Processed Time: {result.processed_time}</p>
                    <p>MGRS: {result.MGRS}</p>
                  </li>
                ))}
              </ul>
              {results.length > currentPage * 10 && (
                <button className="next-button" onClick={() => setCurrentPage(currentPage + 1)}>Next</button>
              )}
            </div>
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
