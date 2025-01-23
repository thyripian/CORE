// App.js
import React, { useState, useEffect, useRef } from 'react';
import { Routes, Route, Link, useLocation } from 'react-router-dom';
import axios from 'axios';
import HomeComponent from './components/HomeComponent';
import SearchComponent from './components/SearchComponent';
import SearchResultsComponent from './components/SearchResultsComponent';
import UpdateCheckerComponent from './components/UpdateCheckerComponent';
import AboutComponent from './components/AboutComponent';
import ContactComponent from './components/ContactComponent';
import HistoryComponent from './components/HistoryComponent';
import SettingsComponent from './components/SettingsComponent';
import LoadingSpinner from './components/LoadingSpinner';
import FullReportComponent from './components/FullReportComponent';
import './App.css';

const App = () => {
  const [menuOpen, setMenuOpen] = useState(false);
  const location = useLocation();
  const menuRef = useRef(null);

  // Initialization state variables
  const [isInitialized, setIsInitialized] = useState(false);
  const [initializationMessage, setInitializationMessage] = useState('');
  const [error, setError] = useState(null);

  // State variables to check readiness of specific services
  const [searchApiReady, setSearchApiReady] = useState(false);
  const [updateApiReady, setUpdateApiReady] = useState(false);

  const toggleMenu = () => {
    setMenuOpen(!menuOpen);
  };

  const handleClickOutside = (event) => {
    if (menuRef.current && !menuRef.current.contains(event.target)) {
      setMenuOpen(false);
    }
  };

  useEffect(() => {
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Only check for main backend readiness on app load
  useEffect(() => {
    let isCancelled = false;
    const timeoutDuration = 60000; // 60 seconds
    const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));
    const startTime = Date.now();

    const initializeBackend = async () => {
      try {
        setInitializationMessage('Initializing central backend API...');
        while (!isCancelled) {
          try {
            const response = await axios.post('http://localhost:5005/api/initialize');
            if (response.data.status === "success") {
              console.log("Central backend initialized successfully");
              setIsInitialized(true);
              break; // Proceed as main backend is ready
            } else {
              console.error("Central backend initialization failed:", response.data.message);
            }
          } catch (error) {
            console.error("Error initializing central backend:", error);
          }

          // Check for timeout
          if (Date.now() - startTime > timeoutDuration) {
            setError('Initialization is taking longer than expected. Please try again later.');
            return;
          }

          // Wait before retrying
          await delay(1000);
        }
      } catch (error) {
        console.error("Unexpected error during initialization:", error);
        if (!isCancelled) {
          setError('An unexpected error occurred during initialization.');
        }
      }
    };

    initializeBackend();

    return () => {
      isCancelled = true;
    };
  }, []); // Run once on component mount

  // Helper function to check specific API readiness
  const checkApiReadiness = async (apiUrl, setReadyState) => {
    try {
      const response = await axios.get(apiUrl);
      if (response.data.status === 'ready') {
        setReadyState(true);
      } else {
        console.log(`${apiUrl} not ready yet.`);
      }
    } catch (error) {
      console.error(`Error checking ${apiUrl} status:`, error);
    }
  };

  const handleNavigateToSearch = () => {
    if (!searchApiReady) {
      checkApiReadiness('http://localhost:5000/api/status', setSearchApiReady);
    }
  };

  const handleNavigateToUpdate = () => {
    if (!updateApiReady) {
      checkApiReadiness('http://localhost:5001/api/status', setUpdateApiReady);
    }
  };

  const getPageClass = () => {
    if (!isInitialized) return 'loading'; // Return 'loading' class when not initialized
    if (location.pathname === '/about') return 'about';
    if (location.pathname === '/contact') return 'contact';
    if (location.pathname === '/history') return 'history';
    if (location.pathname === '/results') return 'results';
    if (location.pathname === '/settings') return 'settings';
    if (location.pathname === '/') return 'home';
    return '';
  };

  return (
    <div className="App">
      <img
        src={`${process.env.PUBLIC_URL}/CORE_logo_no-words.png`}
        alt="Background"
        className={`background-image ${getPageClass()}`}
      />

      {error ? (
        <div className="error-message">{error}</div>
      ) : !isInitialized ? (
        <LoadingSpinner message={initializationMessage} />
      ) : (
        <>
          <header className="App-header">
            <Link to="/" className="home-icon">
              <img src={`${process.env.PUBLIC_URL}/blk_home.png`} alt="Home" />
            </Link>
            <div className="menu-icon">
              <img src={`${process.env.PUBLIC_URL}/menu.png`} alt="Menu" onClick={toggleMenu} />
            </div>
            <Link to="/settings" className="settings-icon">
              <img src={`${process.env.PUBLIC_URL}/gear1a.png`} alt="Settings" />
            </Link>
            {menuOpen && (
              <div className="dropdown-menu" ref={menuRef}>
                <Link to="/about" onClick={() => setMenuOpen(false)}>About</Link>
                <Link to="/contact" onClick={() => setMenuOpen(false)}>Contact/Help</Link>
                <Link to="/history" onClick={() => setMenuOpen(false)}>History</Link>
              </div>
            )}
            <div className="App-title">
              <h1>CORE</h1>
            </div>
            <nav>
              <Link to="/search" onClick={handleNavigateToSearch}>Search</Link>
              <Link to="/updates" onClick={handleNavigateToUpdate}>Check for Updates</Link>
            </nav>
          </header>
          <div className="hidden-buffer"></div>
          <main className="App-main">
            <Routes>
              <Route path="/" element={<HomeComponent />} />
              <Route
                path="/search"
                element={
                  searchApiReady ? (
                    <SearchComponent />
                  ) : (
                    <LoadingSpinner message="Initializing Search API..." />
                  )
                }
              />
              <Route path="/results" element={<SearchResultsComponent />} />
              <Route
                path="/updates"
                element={
                  updateApiReady ? (
                    <UpdateCheckerComponent />
                  ) : (
                    <LoadingSpinner message="Initializing Update API..." />
                  )
                }
              />
              <Route path="/about" element={<AboutComponent />} />
              <Route path="/contact" element={<ContactComponent />} />
              <Route path="/history" element={<HistoryComponent />} />
              <Route path="/settings" element={<SettingsComponent />} />
              <Route path="/view-report/:hash" element={<FullReportComponent />} />
            </Routes>
          </main>
        </>
      )}
    </div>
  );
};

export default App;
