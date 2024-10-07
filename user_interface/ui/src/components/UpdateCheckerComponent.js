import React, { useState, useEffect } from 'react';
import '../styles/UpdateCheckerComponent.css';

const CheckForUpdates = () => {
  const [processing, setProcessing] = useState(false);
  const [progress, setProgress] = useState({ current: 0, total: 0, message: 'Not started' });
  const [error, setError] = useState(null);

  const checkForUpdates = async () => {
    setProcessing(true);
    try {
      const response = await fetch('http://localhost:5001/api/check-for-updates', { method: 'POST' });
      if (!response.ok) {
        console.error('Network response was not ok:', response.statusText);
        throw new Error('Network response was not ok');
      }
      const data = await response.json();
      console.log('Update process started:', data);
    } catch (err) {
      console.error('Failed to check for updates:', err);
      setError('Failed to start update process');
      setProcessing(false); // Reset processing state on error
    }
  };

  useEffect(() => {
    let interval;
    if (processing) {
      interval = setInterval(async () => {
        try {
          const response = await fetch('http://localhost:5001/api/progress');
          if (!response.ok) {
            console.error('Network response was not ok:', response.statusText);
            throw new Error('Network response was not ok');
          }
          const data = await response.json();
          setProgress(data);

          // Stop polling if the process is completed
          if (data.message === 'Completed' || data.message.startsWith('Failed')) {
            setProcessing(false);
            clearInterval(interval);
          }
        } catch (err) {
          console.error('Failed to fetch progress data:', err);
          setError('Failed to fetch progress data');
          setProcessing(false);
          clearInterval(interval);
        }
      }, 2200); // Poll every 2.2 seconds
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [processing]);

  return (
    <div>
      <button onClick={checkForUpdates} disabled={processing} className="update-button">
        {processing ? 'Processing...' : 'Check for Updates'}
      </button>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {processing && (
        <div>
          <p>{progress.message}</p>
          <progress value={progress.current} max={progress.total}></progress>
          <p>{progress.current} / {progress.total}</p>
        </div>
      )}
    </div>
  );
};

export default CheckForUpdates;
