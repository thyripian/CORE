import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/SearchComponent.css'; // Import the CSS file for styling

function SearchComponent() {
  const [query, setQuery] = useState('');
  const navigate = useNavigate(); // Hook to navigate to different routes

  const handleSearch = () => {
    // Navigate to the search results page with the query as a state
    if (query.trim()) {
      navigate('/results', { state: { query } });
    }
  };

  return (
    <div className="page-content">
      <div className="search-container">
        <div className="search-box">
          <input 
            type="text" 
            value={query} 
            onChange={(e) => setQuery(e.target.value)} 
            className="search-input" 
            placeholder="Search..."
          />
          <button onClick={handleSearch} className="search-button">Search</button>
        </div>
      </div>
    </div>
  );
}

export default SearchComponent;
