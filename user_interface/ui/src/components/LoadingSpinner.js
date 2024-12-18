// import React from 'react';
// import '../styles/LoadingSpinner.css';

// function LoadingSpinner({ message }) {
//   return (
//     <div className="loading-spinner-container">
//       <h1><b>Initializing CORE</b></h1>
//       <p>{message}</p>
//       <div className="loading-spinner"></div>
//     </div>
//   );
// }

// export default LoadingSpinner;

import React from 'react';
import '../styles/LoadingSpinner.css';

function LoadingSpinner({ message, subMessage }) {
  return (
    <div className="loading-spinner-container">
      <h1><b>Initializing CORE</b></h1>
      <p>{message}</p>
      {subMessage && <p>{subMessage}</p>}
      <div className="loading-spinner"></div>
    </div>
  );
}

export default LoadingSpinner;
