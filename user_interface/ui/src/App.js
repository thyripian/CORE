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
import './App.css';

const App = () => {
  const [menuOpen, setMenuOpen] = useState(false);
  const location = useLocation();
  const menuRef = useRef(null);

  // Initialization state variables
  const [isInitialized, setIsInitialized] = useState(false);
  const [initializationMessage, setInitializationMessage] = useState('');
  const [error, setError] = useState(null);

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

  useEffect(() => {
    let isCancelled = false;
    const timeoutDuration = 60000; // 60 seconds
    const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));
    const startTime = Date.now();

    const initializeSequentially = async () => {
      try {
        // Step 1: Initialize central backend
        setInitializationMessage('Initializing central backend API...');
        while (!isCancelled) {
          try {
            const response = await axios.post('http://localhost:5005/initialize');
            if (response.data.status === "success") {
              console.log("Central backend initialized successfully");
              break; // Proceed to next step
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

        if (isCancelled) return;

        // Step 2: Initialize search API
        setInitializationMessage('Initializing search API...');
        while (!isCancelled) {
          try {
            const response = await axios.get('http://localhost:5000/status');
            if (response.data.status === 'ready') {
              console.log("Search API initialized successfully");
              break; // Proceed to next step
            } else {
              console.log("Search API not ready yet.");
            }
          } catch (error) {
            console.error("Error checking search API status:", error);
          }

          // Check for timeout
          if (Date.now() - startTime > timeoutDuration) {
            setError('Initialization is taking longer than expected. Please try again later.');
            return;
          }

          // Wait before retrying
          await delay(1000);
        }

        if (isCancelled) return;

        // Step 3: Initialize update API
        setInitializationMessage('Initializing update API...');
        while (!isCancelled) {
          try {
            const response = await axios.get('http://localhost:5001/status');
            if (response.data.status === 'ready') {
              console.log("Update API initialized successfully");
              break; // All done
            } else {
              console.log("Update API not ready yet.");
            }
          } catch (error) {
            console.error("Error checking update API status:", error);
          }

          // Check for timeout
          if (Date.now() - startTime > timeoutDuration) {
            setError('Initialization is taking longer than expected. Please try again later.');
            return;
          }

          // Wait before retrying
          await delay(1000);
        }

        if (isCancelled) return;

        // All initializations complete
        setIsInitialized(true);
      } catch (error) {
        console.error("Unexpected error during initialization:", error);
        if (!isCancelled) {
          setError('An unexpected error occurred during initialization.');
        }
      }
    };

    initializeSequentially();

    // Set a timeout to cancel the initialization after timeoutDuration
    const timeout = setTimeout(() => {
      if (!isInitialized) {
        setError('Initialization is taking longer than expected. Please try again later.');
      }
    }, timeoutDuration);

    return () => {
      isCancelled = true;
      clearTimeout(timeout); // Clear timeout when component unmounts
    };
  }, [isInitialized]); // Re-run this effect only when isInitialized changes


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
              <Link to="/search">Search</Link>
              <Link to="/updates">Check for Updates</Link>
            </nav>
          </header>
          <div className="hidden-buffer"></div>
          <main className="App-main">
            <Routes>
              <Route path="/" element={<HomeComponent />} />
              <Route path="/search" element={<SearchComponent />} />
              <Route path="/results" element={<SearchResultsComponent />} />
              <Route path="/updates" element={<UpdateCheckerComponent />} />
              <Route path="/about" element={<AboutComponent />} />
              <Route path="/contact" element={<ContactComponent />} />
              <Route path="/history" element={<HistoryComponent />} />
              <Route path="/settings" element={<SettingsComponent />} />
            </Routes>
          </main>
        </>
      )}
    </div>
  );
};

export default App;
