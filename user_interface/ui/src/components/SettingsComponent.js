import React, { useState } from 'react';
import axios from 'axios';
import { Collapse } from 'react-collapse';
import '../styles/SettingsComponent.css';
import { FaEye, FaEyeSlash, FaSave, FaFolderOpen } from 'react-icons/fa';

const SettingsComponent = () => {
  const [settings, setSettings] = useState({
    directory: "",
    user_config: {
      postgres: {
        minconn: "",
        maxconn: "",
        user: "",
        password: "",
        host: "",
        port: "",
        database: ""
      },
      elasticsearch: {
        hosts: [""],
        user: "",
        password: "",
        verify_certs: true,
        ca_certs: "",
        index: ""
      },
      sqlite: {
        sqlite_directory: ""
      },
      keywords: {
        keyword_dir: ""
      },
      logging: {
        log_directory: ""
      }
    }
  });

  const [loading, setLoading] = useState(false);
  const [saveStatus, setSaveStatus] = useState("");
  const [showPasswords, setShowPasswords] = useState({
    postgres: false,
    elasticsearch: false,
  });
  const [collapseState, setCollapseState] = useState({
    postgres: false,
    elasticsearch: false,
    sqlite: false,
    keywords: false,
    logging: false,
  });

  // Handler to load settings when the button is clicked
  const loadSettings = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setLoading(true);
    try {
      const text = await file.text();
      const settingsData = JSON.parse(text);

      // Split Elasticsearch basic_auth correctly from the loaded JSON
      if (settingsData.user_config?.elasticsearch?.basic_auth) {
        settingsData.user_config.elasticsearch.user = settingsData.user_config.elasticsearch.basic_auth.user;
        settingsData.user_config.elasticsearch.password = settingsData.user_config.elasticsearch.basic_auth.password;
        delete settingsData.user_config.elasticsearch.basic_auth;
      }

      setSettings(settingsData);
    } catch (error) {
      console.error("Error loading settings:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (section, key, value) => {
    setSettings(prevSettings => ({
      ...prevSettings,
      [section]: {
        ...prevSettings[section],
        [key]: value
      }
    }));
  };

  const toggleShowPassword = (section) => {
    setShowPasswords(prevState => ({
      ...prevState,
      [section]: !prevState[section]
    }));
  };

  const toggleCollapse = (section) => {
    setCollapseState(prevState => ({
      ...prevState,
      [section]: !prevState[section]
    }));
  };

  const saveSettings = async () => {
    const settingsToSave = { ...settings };

    // Nest Elasticsearch user and password fields back under basic_auth
    settingsToSave.user_config.elasticsearch.basic_auth = {
      user: settingsToSave.user_config.elasticsearch.user,
      password: settingsToSave.user_config.elasticsearch.password,
    };
    delete settingsToSave.user_config.elasticsearch.user;
    delete settingsToSave.user_config.elasticsearch.password;

    try {
      await axios.post('/api/save-settings', settingsToSave);
      setSaveStatus("Settings saved successfully!");
    } catch (error) {
      console.error("Error saving settings:", error);
      setSaveStatus("Error saving settings.");
    }
  };

  const handleFileSelect = (section, key) => (event) => {
    const selectedPath = event.target.files[0]?.path || event.target.value;
    handleInputChange(section, key, selectedPath);
  };

  return (
    <div className="settings-content scrollable-container">
      <h2>Settings</h2>

      {/* Save Status Message */}
      {saveStatus && <p className="save-status">{saveStatus}</p>}

      {/* Load Settings Button */}
      <div className="load-button-wrapper">
        <label className="load-button">
          <FaFolderOpen /> Load Settings
          <input
            type="file"
            accept=".json"
            onChange={loadSettings}
            disabled={loading}
            style={{ display: 'none' }}
          />
        </label>
      </div>

      {/* Directory Setting */}
      <div className="settings-section directory-section">
        <h3>General Directory</h3>
        <div className="form-field with-button">
          <label>Path:</label>
          <input
            type="text"
            value={settings.directory}
            onChange={(e) => handleInputChange("directory", "directory", e.target.value)}
            placeholder="Enter directory path"
          />
          <label htmlFor="directory-input" className="select-path-button small-button">
            Select Path
          </label>
          <input
            type="file"
            webkitdirectory=""
            directory=""
            style={{ display: 'none' }}
            id="directory-input"
            onChange={handleFileSelect("directory", "directory")}
          />
        </div>
      </div>

      {/* User Config Section */}
      {settings.user_config && (
        <>
          <div className="settings-section">
            {/* Postgres Settings */}
            <div className="settings-collapsible" onClick={() => toggleCollapse('postgres')}>
              <h3>Postgres Settings</h3>
              <button className="collapse-button">{collapseState.postgres ? 'Hide' : 'Show'}</button>
            </div>
            <Collapse isOpened={collapseState.postgres}>
              <div className="form-fields">
                {Object.keys(settings.user_config.postgres).map((key) => (
                  <div className="form-field" key={`postgres-${key}`}>
                    <label>{key}:</label>
                    <input
                      type={key === 'password' && !showPasswords.postgres ? "password" : "text"}
                      value={settings.user_config.postgres[key]}
                      onChange={(e) => handleInputChange("user_config", "postgres", {
                        ...settings.user_config.postgres,
                        [key]: e.target.value
                      })}
                      placeholder={`Enter ${key}`}
                    />
                    {key === 'password' && (
                      <button
                        type="button"
                        className="toggle-password-button"
                        onClick={() => toggleShowPassword('postgres')}
                      >
                        {showPasswords.postgres ? <FaEyeSlash /> : <FaEye />}
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </Collapse>

            {/* Elasticsearch Settings */}
            <div className="settings-collapsible" onClick={() => toggleCollapse('elasticsearch')}>
              <h3>Elasticsearch Settings</h3>
              <button className="collapse-button">{collapseState.elasticsearch ? 'Hide' : 'Show'}</button>
            </div>
            <Collapse isOpened={collapseState.elasticsearch}>
              <div className="form-fields">
                <div className="form-field">
                  <label>Hosts:</label>
                  <input
                    type="text"
                    value={settings.user_config.elasticsearch.hosts[0]}
                    onChange={(e) => handleInputChange("user_config", "elasticsearch", {
                      ...settings.user_config.elasticsearch,
                      hosts: [e.target.value]
                    })}
                    placeholder="Enter Elasticsearch host"
                  />
                </div>
                <div className="form-field half-width">
                  <label>Basic Auth User:</label>
                  <input
                    type="text"
                    value={settings.user_config.elasticsearch.user}
                    onChange={(e) => handleInputChange("user_config", "elasticsearch", {
                      ...settings.user_config.elasticsearch,
                      user: e.target.value
                    })}
                    placeholder="Enter username"
                  />
                </div>
                <div className="form-field half-width">
                  <label>Basic Auth Password:</label>
                  <input
                    type={showPasswords.elasticsearch ? "text" : "password"}
                    value={settings.user_config.elasticsearch.password}
                    onChange={(e) => handleInputChange("user_config", "elasticsearch", {
                      ...settings.user_config.elasticsearch,
                      password: e.target.value
                    })}
                    placeholder="Enter password"
                  />
                  <button
                    type="button"
                    className="toggle-password-button"
                    onClick={() => toggleShowPassword('elasticsearch')}
                  >
                    {showPasswords.elasticsearch ? <FaEyeSlash /> : <FaEye />}
                  </button>
                </div>
                <div className="form-field">
                  <label>Verify Certificates:</label>
                  <input
                    type="checkbox"
                    checked={settings.user_config.elasticsearch.verify_certs}
                    onChange={(e) => handleInputChange("user_config", "elasticsearch", {
                      ...settings.user_config.elasticsearch,
                      verify_certs: e.target.checked
                    })}
                  />
                </div>
                <div className="form-field">
                  <label>CA Certificates Path:</label>
                  <input
                    type="text"
                    value={settings.user_config.elasticsearch.ca_certs}
                    onChange={(e) => handleInputChange("user_config", "elasticsearch", {
                      ...settings.user_config.elasticsearch,
                      ca_certs: e.target.value
                    })}
                    placeholder="Enter CA certificates path"
                  />
                </div>
                <div className="form-field">
                  <label>Index Name:</label>
                  <input
                    type="text"
                    value={settings.user_config.elasticsearch.index}
                    onChange={(e) => handleInputChange("user_config", "elasticsearch", {
                      ...settings.user_config.elasticsearch,
                      index: e.target.value
                    })}
                    placeholder="Enter index name"
                  />
                </div>
              </div>
            </Collapse>

            {/* SQLite Settings */}
            <div className="settings-collapsible" onClick={() => toggleCollapse('sqlite')}>
              <h3>SQLite Settings</h3>
              <button className="collapse-button">{collapseState.sqlite ? 'Hide' : 'Show'}</button>
            </div>
            <Collapse isOpened={collapseState.sqlite}>
              <div className="form-fields">
                <div className="form-field with-button">
                  <label>SQLite Directory:</label>
                  <input
                    type="text"
                    value={settings.user_config.sqlite.sqlite_directory}
                    onChange={(e) => handleInputChange("user_config", "sqlite", {
                      sqlite_directory: e.target.value
                    })}
                    placeholder="Enter SQLite directory path"
                  />
                  <label htmlFor="sqlite-directory-input" className="select-path-button small-button">
                    Select Save Directory
                  </label>
                  <input
                    type="file"
                    webkitdirectory=""
                    directory=""
                    style={{ display: 'none' }}
                    id="sqlite-directory-input"
                    onChange={handleFileSelect("user_config", "sqlite")}
                  />
                </div>
              </div>
            </Collapse>

            {/* Keywords Settings */}
            <div className="settings-collapsible" onClick={() => toggleCollapse('keywords')}>
              <h3>Keywords Settings</h3>
              <button className="collapse-button">{collapseState.keywords ? 'Hide' : 'Show'}</button>
            </div>
            <Collapse isOpened={collapseState.keywords}>
              <div className="form-fields">
                <div className="form-field with-button">
                  <label>Keyword Directory:</label>
                  <input
                    type="text"
                    value={settings.user_config.keywords.keyword_dir}
                    onChange={(e) => handleInputChange("user_config", "keywords", {
                      keyword_dir: e.target.value
                    })}
                    placeholder="Enter keyword directory path"
                  />
                  <label htmlFor="keyword-file-input" className="select-path-button small-button">
                    Select Keywords File
                  </label>
                  <input
                    type="file"
                    style={{ display: 'none' }}
                    id="keyword-file-input"
                    onChange={handleFileSelect("user_config", "keywords")}
                  />
                </div>
              </div>
            </Collapse>
          </div>
        </>
      )}

      {/* Save Button */}
      <button className="save-button" onClick={saveSettings}>
        <FaSave /> Save Settings
      </button>
    </div>
  );
};

export default SettingsComponent;
