import React, { useState, useEffect, useRef } from 'react';
import { Routes, Route, Link, useLocation } from 'react-router-dom';
import axios from 'axios'; // Add axios for making API calls
import HomeComponent from './components/HomeComponent';
import SearchComponent from './components/SearchComponent';
import SearchResultsComponent from './components/SearchResultsComponent';
import UpdateCheckerComponent from './components/UpdateCheckerComponent';
import AboutComponent from './components/AboutComponent';
import ContactComponent from './components/ContactComponent';
import HistoryComponent from './components/HistoryComponent';
import SettingsComponent from './components/SettingsComponent';
import './App.css';

const App = () => {
  const [menuOpen, setMenuOpen] = useState(false);
  const location = useLocation();
  const menuRef = useRef(null);

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

    const [isInitialized, setIsInitialized] = useState(false); // Flag to ensure it's called only once
  
    useEffect(() => {
      const initializeBackend = async () => {
        try {
          if (!isInitialized) {  // Check if already initialized
            const response = await axios.post('http://localhost:5005/initialize'); // Adjust URL if needed
            if (response.data.status === "success") {
              console.log("Backend initialized successfully");
              setIsInitialized(true);  // Set flag to true after successful initialization
            } else {
              console.error("Backend initialization failed:", response.data.message);
            }
          } else {
            console.log("Backend is already initialized");
          }
        } catch (error) {
          console.error("Error initializing backend:", error);
        }
      };
  
      initializeBackend();  // Call backend initialization on app load
    }, [isInitialized]);

  const getPageClass = () => {
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
    </div>
  );
}

export default App;
