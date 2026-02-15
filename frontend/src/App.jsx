import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Sidebar } from './components/Sidebar';
import { TopBar } from './components/TopBar';
import { MainContent } from './components/MainContent';

function App() {
  const [activeView, setActiveView] = useState('overview');
  const [status, setStatus] = useState('disconnected'); // 'connected' | 'disconnected' (Backend health)
  const [balance, setBalance] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const BACKEND_URL = 'http://127.0.0.1:8000';

  // Poll backend health
  useEffect(() => {
    const checkBackendStatus = async () => {
      try {
        await axios.get(`${BACKEND_URL}/`);
        setStatus('connected');
      } catch (error) {
        setStatus('disconnected');
      }
    };

    // Check immediately
    checkBackendStatus();

    // Check every 5 seconds
    const interval = setInterval(checkBackendStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  // Handle Get Trading212 Info
  const handleGetTrading212Info = async () => {
    setIsLoading(true);
    try {
      const response = await axios.post(`${BACKEND_URL}/scrape/t212`);
      if (response.data.status === 'success') {
        const cash = response.data.cash;
        // cash example: {'free': 100, 'total': 1000, ...}
        let val = cash?.total ?? 0;
        setBalance(val);
        alert("Trading212 data synced successfully!");
      }
    } catch (error) {
      console.error("Trading212 Sync failed", error);
      const detail = error.response?.data?.detail || error.message;

      if (error.response?.status === 400 && detail.includes("API Keys missing")) {
        if (confirm("API Keys are missing. Go to Settings to configure them?")) {
          setActiveView('settings'); // Placeholder for redirect
        }
      } else {
        alert("Failed to get Trading212 Info: " + detail);
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Handle Get Stock Info
  const handleGetStockInfo = async () => {
    setIsLoading(true);
    try {
      await axios.post(`${BACKEND_URL}/scrape/yfinance`);
      alert("Stock info updated successfully!");
    } catch (error) {
      console.error("Stock Sync failed", error);
      const detail = error.response?.data?.detail || error.message;

      if (error.response?.status === 400 && (detail.includes("not found") || detail.includes("is empty"))) {
        if (confirm("Tickers list is missing or empty. Go to Settings to configure tickers?")) {
          setActiveView('settings'); // Placeholder for redirect
        }
      } else {
        alert("Failed to get Stock Info: " + detail);
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-background text-text-main overflow-hidden font-sans">

      {/* Sidebar Navigation */}
      <Sidebar
        activeView={activeView}
        setActiveView={setActiveView}
      />

      {/* Main Column */}
      <div className="flex-1 flex flex-col min-w-0">

        {/* Top Action Bar */}
        <TopBar
          status={status}
          balance={balance}
          onConnect={handleGetTrading212Info}
          onDisconnect={handleGetStockInfo}
          isLoading={isLoading}
        />

        {/* Content Area */}
        <MainContent activeView={activeView} />

      </div>
    </div>
  );
}

export default App;
