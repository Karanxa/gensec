// App.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
  const [prompt, setPrompt] = useState('');
  const [results, setResults] = useState([]);

  useEffect(() => {
    fetchResults();
  }, []);

  const fetchResults = async () => {
    const response = await axios.get('http://localhost:5000/api/results');
    setResults(response.data);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post('http://localhost:5000/api/fuzz', { prompt });
      setPrompt('');
      fetchResults();
    } catch (error) {
      console.error('Error submitting prompt:', error);
    }
  };

  return (
    <div className="App">
      <h1>Prompt Fuzzing App</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Enter your prompt"
        />
        <button type="submit">Submit</button>
      </form>
      <h2>Results:</h2>
      <ul>
        {results.map((result, index) => (
          <li key={index}>
            <strong>Prompt:</strong> {result.prompt}<br />
            <strong>Response:</strong> {result.response}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;