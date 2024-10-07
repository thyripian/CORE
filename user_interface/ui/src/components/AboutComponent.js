import React from 'react';
import '../styles/AboutComponent.css';

const AboutComponent = () => {
  return (
    <div className="about-content">
      <h2>About CORE</h2>
      <p>
          This application was developed for centralized operational reporting of diverse datasets.<br/>
          It was initially created to facilitate databasing and querying Word documents, Excel spreadsheets,<br/>
          PowerPoint presentations, and Adobe PDFs that were stored on shared drives, providing an efficient way to<br/>
          manage and search through large collections of files without a practical solution in place.
      </p>
    </div>
  );
};

export default AboutComponent;
