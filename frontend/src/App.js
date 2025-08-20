import React, { useState, useEffect } from 'react';
import { ConfigProvider } from 'antd';
import frFR from 'antd/locale/fr_FR';
import Dashboard from './components/Dashboard';
import Login from './components/Login';
import 'antd/dist/reset.css';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    setIsAuthenticated(!!token);
    setLoading(false);
  }, []);

  const handleLogin = () => {
    setIsAuthenticated(true);
  };

  if (loading) {
    return <div>Chargement...</div>;
  }

  return (
    <ConfigProvider locale={frFR}>
      <div className="App">
        {isAuthenticated ? (
          <Dashboard />
        ) : (
          <Login onLogin={handleLogin} />
        )}
      </div>
    </ConfigProvider>
  );
}

export default App;