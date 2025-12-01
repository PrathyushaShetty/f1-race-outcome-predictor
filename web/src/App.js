import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';

// Components
import Header from './components/Header';
import Footer from './components/Footer';
import SplashScreen from './components/SplashScreen';
import Dashboard from './pages/Dashboard';
import LiveRace from './pages/LiveRace';
import Predictions from './pages/Predictions';
import Leaderboard from './pages/Leaderboard';

function App() {
  const [showSplash, setShowSplash] = useState(true);

  return (
    <>
      {showSplash && <SplashScreen onFinish={() => setShowSplash(false)} />}
      <Router>
        <div className={`App min-h-screen bg-gray-100 ${showSplash ? 'hidden' : ''}`}>
          <Header />

          <main className="container mx-auto px-4 py-8">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/live" element={<LiveRace />} />
              <Route path="/predictions" element={<Predictions />} />
              <Route path="/leaderboard" element={<Leaderboard />} />
            </Routes>
          </main>

          <Footer />
        </div>
      </Router>
    </>
  );
}

export default App;
