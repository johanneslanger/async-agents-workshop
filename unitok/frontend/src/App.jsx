import axios from 'axios';
import { useEffect, useState } from 'react';
import './App.css';
import Feed from './components/Feed';
import Header from './components/Header';

function App() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [config, setConfig] = useState(null);

  // Load configuration
  useEffect(() => {
    const loadConfig = async () => {
      try {
        const response = await axios.get('/config.json');
        setConfig(response.data);
      } catch (err) {
        console.error('Failed to load config:', err);
        setConfig({ apiEndpoint: 'http://localhost:3001' }); // Fallback for local development
      }
    };
    
    loadConfig();
  }, []);

  // Fetch posts when config is loaded
  useEffect(() => {
    if (!config) return;
    
    const fetchPosts = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`${config.apiEndpoint}/posts`);
        setPosts(response.data);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching posts:', err);
        setError('Failed to load posts. Please try again later.');
        setLoading(false);
      }
    };
    
    fetchPosts();
  }, [config]);

  return (
    <div className="app">
      <Header />
      <main className="main-content">
        {loading ? (
          <div className="loading">
            <div className="loading-spinner"></div>
            <p>Loading magical unicorn posts...</p>
          </div>
        ) : error ? (
          <div className="error-message">
            <p>{error}</p>
            <button onClick={() => window.location.reload()}>Try Again</button>
          </div>
        ) : (
          <Feed posts={posts} />
        )}
      </main>
      <footer className="footer">
        <p>This is a dummy Unicorn Rentals Social Media site</p>
      </footer>
    </div>
  );
}

export default App;
