// import React, { useState, useEffect } from 'react';
// import { useLocation, useNavigate } from 'react-router-dom';
// import LeafletMapComponent from './LeafletMapComponent';
// import '../styles/SearchResultsComponent.css';

// function SearchResultsComponent() {
//   const location = useLocation();
//   const navigate = useNavigate();

//   const initialQuery = location.state?.query || '';
//   const [query, setQuery] = useState(initialQuery);
//   const [results, setResults] = useState([]);
//   const [loading, setLoading] = useState(false);
//   const [error, setError] = useState(null);
//   const [viewMode, setViewMode] = useState('list');
//   const [currentPage, setCurrentPage] = useState(1);

//   useEffect(() => {
//     if (initialQuery) {
//       setLoading(true);
//       setError(null);
//       fetch(`http://localhost:5000/api/search?query=${encodeURIComponent(initialQuery)}`)
//         .then(async response => {
//           if (!response.ok) {
//             throw new Error(`HTTP error! status: ${response.status}`);
//           }
//           const data = await response.json();
//           setResults(data.records);
//         })
//         .catch(err => {
//           setError(`An error occurred: ${err.message}`);
//         })
//         .finally(() => {
//           setLoading(false);
//         });
//     }
//   }, [initialQuery]);

//   const handleSearch = () => {
//     if (query.trim()) {
//       setResults([]);
//       setLoading(true);
//       setError(null);
//       fetch(`http://localhost:5000/api/search?query=${encodeURIComponent(query)}`)
//         .then(async response => {
//           if (!response.ok) {
//             throw new Error(`HTTP error! status: ${response.status}`);
//           }
//           const data = await response.json();
//           setResults(data.records);
//         })
//         .catch(err => {
//           setError(`An error occurred: ${err.message}`);
//         })
//         .finally(() => {
//           setLoading(false);
//         });
//     }
//   };

//   const handleKeyDown = (e) => {
//     if (e.key === 'Enter') {
//       handleSearch();
//     }
//   };

//   // Basic map config
//   const center = { lat: 37.7749, lng: -122.4194 };
//   const markers = results
//     .filter(result => result.lat && result.lng)
//     .map(result => ({ lat: result.lat, lng: result.lng, name: result.name }));

//   // Navigate to a full report view
//   const handleViewFullReport = (hash) => {
//     // Suppose record.file_hash holds the unique hash
//     navigate(`/view-report/${hash}`);
//   };

//   return (
//     <div className="results-container">
//       <div className="search-box-wrapper">
//         <div className="search-box">
//           <input
//             type="text"
//             value={query}
//             onChange={(e) => setQuery(e.target.value)}
//             onKeyDown={handleKeyDown}
//             className="search-input"
//             placeholder="Search..."
//           />
//           <button
//             onClick={() => {
//               handleSearch();
//               setCurrentPage(1);
//             }}
//             className="search-button"
//           >
//             Search
//           </button>
//         </div>
//         <div className="view-toggle">
//           <button
//             className={`view-button ${viewMode === 'list' ? 'active' : ''}`}
//             onClick={() => setViewMode('list')}
//           >
//             List View
//           </button>
//           <button
//             className={`view-button ${viewMode === 'map' ? 'active' : ''}`}
//             onClick={() => setViewMode('map')}
//           >
//             Map View
//           </button>
//         </div>
//       </div>
//       {loading && <p>Loading...</p>}
//       {error && <p>Error: {error}</p>}
//       <div className="search-results">
//         {viewMode === 'list' ? (
//           results.length > 0 ? (
//             <div className="results-list-container">
//               <ul className="results-content">
//                 {results
//                   .slice((currentPage - 1) * 10, currentPage * 10)
//                   .map((result, index) => {
//                     // Show a small snippet of the full_text
//                     const fullText = result.full_text || '';
//                     const snippet = fullText.length > 200
//                       ? fullText.substring(0, 200) + '...'
//                       : fullText;

//                     return (
//                       <li
//                         key={index}
//                         className="result-item"
//                         onClick={() => handleViewFullReport(result.SHA256_hash)}
//                         style={{ cursor: 'pointer' }}
//                       >
//                         <p><strong>Classification:</strong> {result.highest_classification}</p>
//                         <p><strong>File:</strong> {result.file_path}</p>
//                         <p><strong>Timeframes:</strong> {result.timeframes ? result.timeframes.join(', ') : 'N/A'}</p>
//                         <p><strong>Locations:</strong> {result.locations ? result.locations.join(', ') : 'N/A'}</p>
//                         <p><strong>MGRS:</strong> {result.MGRS}</p>
//                         <p><strong>Subjects:</strong> {result.subjects}</p>
//                         <p><strong>Snippet:</strong> {snippet}</p>
//                       </li>
//                     );
//                   })}
//               </ul>
//               {results.length > currentPage * 10 && (
//                 <button className="next-button" onClick={() => setCurrentPage(currentPage + 1)}>
//                   Next
//                 </button>
//               )}
//             </div>
//           ) : (
//             !loading && <p>No results found</p>
//           )
//         ) : (
//           <LeafletMapComponent center={center} markers={markers} />
//         )}
//       </div>
//     </div>
//   );
// }

// export default SearchResultsComponent;

import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import LeafletMapComponent from './LeafletMapComponent';
import '../styles/SearchResultsComponent.css';

function SearchResultsComponent() {
  const location = useLocation();
  const navigate = useNavigate();

  // Get the initial query from location state (if available)
  const initialQuery = location.state?.query || '';

  // `query` is for the input field; `activeQuery` is the one we use to fetch results.
  const [query, setQuery] = useState(initialQuery);
  const [activeQuery, setActiveQuery] = useState(initialQuery);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState('list');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalResults, setTotalResults] = useState(0);
  const [totalPages, setTotalPages] = useState(1);

  // Fetch results whenever activeQuery or currentPage changes.
  useEffect(() => {
    if (activeQuery) {
      setLoading(true);
      setError(null);

      fetch(`http://localhost:5000/api/search?query=${encodeURIComponent(activeQuery)}&page=${currentPage}`)
        .then(async response => {
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          const data = await response.json();
          setResults(data.records);
          setTotalResults(data.total_hits);
          setTotalPages(Math.ceil(data.total_hits / 10)); // Assume 10 results per page
        })
        .catch(err => {
          setError(`An error occurred: ${err.message}`);
        })
        .finally(() => {
          setLoading(false);
        });
    }
  }, [activeQuery, currentPage]);

  // When the user performs a new search, update activeQuery and reset the page.
  const handleSearch = () => {
    if (query.trim()) {
      // Reset results and page, then update the active query.
      setResults([]);
      setCurrentPage(1);
      setActiveQuery(query);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  // Navigate to full report view
  const handleViewFullReport = (hash) => {
    navigate(`/view-report/${hash}`);
  };

  // Handle Pagination
  const handlePageChange = (newPage) => {
    console.log(`Changing to page: ${newPage}`);
    if (newPage > 0 && newPage <= totalPages) {
      setCurrentPage(newPage);
    }
  };

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
          <button
            onClick={handleSearch}
            className="search-button"
          >
            Search
          </button>
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

      <div className="total-results">
        <p><strong>Total Results:</strong> {totalResults} | <strong>Pages:</strong> {totalPages}</p>
      </div>

      <div className="search-results">
        {viewMode === 'list' ? (
          results.length > 0 ? (
            <div className="results-list-container">
              <ul className="results-content">
                {results.map((result, index) => {
                  const fileName = result.file_path.split(/[/\\]/).pop(); // Extract file name
                  const snippet = result.full_text?.substring(0, 200) + '...' || 'No snippet available';

                  return (
                    <li
                      key={index}
                      className="result-item"
                      onClick={() => handleViewFullReport(result.SHA256_hash)}
                      style={{ cursor: 'pointer' }}
                    >
                      <p><strong>Classification:</strong> {result.highest_classification}</p>
                      <p><strong>File:</strong> {fileName}</p>
                      <p><strong>Timeframes:</strong> {result.timeframes ? result.timeframes.join(', ') : 'N/A'}</p>
                      <p><strong>Locations:</strong> {result.locations ? result.locations.join(', ') : 'N/A'}</p>
                      <p><strong>MGRS:</strong> {result.MGRS}</p>
                      <p><strong>Subjects:</strong> {result.subjects}</p>
                      <p><strong>Snippet:</strong> {snippet}</p>
                    </li>
                  );
                })}
              </ul>

              {/* Pagination Controls */}
              <div className="pagination">
                {currentPage > 1 && (
                  <button
                    className="pagination-button"
                    onClick={() => handlePageChange(currentPage - 1)}
                  >
                    Previous
                  </button>
                )}

                {currentPage < totalPages && (
                  <button
                    className="pagination-button"
                    onClick={() => handlePageChange(currentPage + 1)}
                  >
                    Next
                  </button>
                )}
              </div>
            </div>
          ) : (
            !loading && <p>No results found</p>
          )
        ) : (
          <LeafletMapComponent />
        )}
      </div>
    </div>
  );
}

export default SearchResultsComponent;
