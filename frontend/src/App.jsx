import React, { useState } from 'react';
import AudioRecorder from './components/AudioRecorder';
import DataForm from './components/DataForm';

function App() {
  const [formData, setFormData] = useState({
    age: '',
    gender: '',
    symptoms: ''
  });
  const [audioBlob, setAudioBlob] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  // In production, this should be the Render URL
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const handleAudioReady = (blob) => {
    setAudioBlob(blob);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!audioBlob) {
      setError('Please record an audio sample first.');
      return;
    }
    if (!formData.age || !formData.gender) {
      setError('Please fill out age and gender.');
      return;
    }

    setError(null);
    setIsLoading(true);

    try {
      const submitData = new FormData();
      submitData.append('audio', audioBlob, 'recording.wav');
      submitData.append('age', formData.age);
      submitData.append('gender', formData.gender);
      submitData.append('symptoms', formData.symptoms);

      const response = await fetch(`${API_URL}/predict`, {
        method: 'POST',
        body: submitData,
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();
      setResult(data.prediction);
    } catch (err) {
      console.error(err);
      setError('Failed to connect to the server. Is the API running?');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header>
        <h1>AIRS Diagnostic</h1>
        <h2>Respiratory Disease Classifier</h2>
      </header>

      <main>
        {error && (
          <div className="card" style={{ borderLeft: '4px solid var(--danger)' }}>
            <p style={{ color: 'var(--danger)', fontWeight: '500' }}>{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="card">
            <h3 style={{ marginBottom: '1rem', color: 'var(--text-primary)' }}>1. Patient Data</h3>
            <DataForm formData={formData} setFormData={setFormData} />
          </div>

          <div className="card">
            <h3 style={{ marginBottom: '1rem', color: 'var(--text-primary)' }}>2. Respiratory Audio</h3>
            <AudioRecorder onAudioReady={handleAudioReady} />
          </div>

          <button 
            type="submit" 
            className="btn btn-primary" 
            disabled={isLoading || !audioBlob}
            style={{ marginBottom: '2rem' }}
          >
            {isLoading ? 'Analyzing...' : 'Analyze Data'}
          </button>
        </form>

        {result && (
          <div className="card results-container">
            <h3 style={{ marginBottom: '1rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>
              Diagnostic Results
            </h3>
            <div className="result-row">
              <span className="result-label">Diagnosis</span>
              <span className={`result-value ${result.diagnosis === 'Positive' ? 'positive' : 'negative'}`}>
                {result.diagnosis}
              </span>
            </div>
            <div className="result-row">
              <span className="result-label">Probability</span>
              <span className="result-value">{(result.disease_probability * 100).toFixed(1)}%</span>
            </div>
            <div className="result-row">
              <span className="result-label">Confidence</span>
              <span className="result-value">{result.confidence}</span>
            </div>
            <div className="result-row">
              <span className="result-label">Model Engine</span>
              <span className="result-value" style={{ fontSize: '0.85rem' }}>{result.model_version}</span>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
