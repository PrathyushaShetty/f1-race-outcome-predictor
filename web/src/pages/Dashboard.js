import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './Dashboard.css';

function Dashboard() {
  const [isLoaded, setIsLoaded] = useState(false);
  const [selectedRace, setSelectedRace] = useState('bahrain-2025');
  const [prediction, setPrediction] = useState({
    winner: 'Max Verstappen',
    team: 'Red Bull Racing',
    confidence: 78,
    podium: [
      { position: 1, driver: 'Max Verstappen', team: 'Red Bull', probability: 35, color: '#0600EF' },
      { position: 2, driver: 'Charles Leclerc', team: 'Ferrari', probability: 28, color: '#DC0000' },
      { position: 3, driver: 'Lewis Hamilton', team: 'Mercedes', probability: 22, color: '#00D2BE' }
    ]
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Available races for 2025 season
  const availableRaces = [
    { id: 'bahrain-2025', name: 'Bahrain Grand Prix', circuit: 'Bahrain International Circuit', country: 'Bahrain', flag: '🇧🇭', date: 'March 2, 2025' },
    { id: 'saudi-2025', name: 'Saudi Arabian Grand Prix', circuit: 'Jeddah Corniche Circuit', country: 'Saudi Arabia', flag: '🇸🇦', date: 'March 9, 2025' },
    { id: 'australia-2025', name: 'Australian Grand Prix', circuit: 'Albert Park Circuit', country: 'Australia', flag: '🇦🇺', date: 'March 16, 2025' },
    { id: 'japan-2025', name: 'Japanese Grand Prix', circuit: 'Suzuka Circuit', country: 'Japan', flag: '🇯🇵', date: 'March 30, 2025' },
    { id: 'china-2025', name: 'Chinese Grand Prix', circuit: 'Shanghai International Circuit', country: 'China', flag: '🇨🇳', date: 'April 6, 2025' },
    { id: 'miami-2025', name: 'Miami Grand Prix', circuit: 'Miami International Autodrome', country: 'USA', flag: '🇺🇸', date: 'May 4, 2025' },
    { id: 'monaco-2025', name: 'Monaco Grand Prix', circuit: 'Circuit de Monaco', country: 'Monaco', flag: '🇲🇨', date: 'May 25, 2025' },
    { id: 'spain-2025', name: 'Spanish Grand Prix', circuit: 'Circuit de Barcelona-Catalunya', country: 'Spain', flag: '🇪🇸', date: 'June 1, 2025' },
    { id: 'canada-2025', name: 'Canadian Grand Prix', circuit: 'Circuit Gilles Villeneuve', country: 'Canada', flag: '🇨🇦', date: 'June 15, 2025' },
    { id: 'austria-2025', name: 'Austrian Grand Prix', circuit: 'Red Bull Ring', country: 'Austria', flag: '🇦🇹', date: 'June 29, 2025' },
    { id: 'britain-2025', name: 'British Grand Prix', circuit: 'Silverstone Circuit', country: 'Great Britain', flag: '🇬🇧', date: 'July 6, 2025' },
    { id: 'belgium-2025', name: 'Belgian Grand Prix', circuit: 'Circuit de Spa-Francorchamps', country: 'Belgium', flag: '🇧🇪', date: 'July 27, 2025' },
    { id: 'netherlands-2025', name: 'Dutch Grand Prix', circuit: 'Circuit Zandvoort', country: 'Netherlands', flag: '🇳🇱', date: 'August 31, 2025' },
    { id: 'italy-2025', name: 'Italian Grand Prix', circuit: 'Autodromo Nazionale di Monza', country: 'Italy', flag: '🇮🇹', date: 'September 7, 2025' },
    { id: 'singapore-2025', name: 'Singapore Grand Prix', circuit: 'Marina Bay Street Circuit', country: 'Singapore', flag: '🇸🇬', date: 'September 21, 2025' },
    { id: 'usa-2025', name: 'United States Grand Prix', circuit: 'Circuit of the Americas', country: 'USA', flag: '🇺🇸', date: 'October 19, 2025' },
    { id: 'mexico-2025', name: 'Mexico City Grand Prix', circuit: 'Autódromo Hermanos Rodríguez', country: 'Mexico', flag: '🇲🇽', date: 'October 26, 2025' },
    { id: 'brazil-2025', name: 'Brazilian Grand Prix', circuit: 'Autódromo José Carlos Pace', country: 'Brazil', flag: '🇧🇷', date: 'November 9, 2025' },
    { id: 'qatar-2025', name: 'Qatar Grand Prix', circuit: 'Losail International Circuit', country: 'Qatar', flag: '🇶🇦', date: 'November 30, 2025' },
    { id: 'abu-dhabi-2025', name: 'Abu Dhabi Grand Prix', circuit: 'Yas Marina Circuit', country: 'UAE', flag: '🇦🇪', date: 'December 7, 2025' }
  ];

  const currentRace = availableRaces.find(race => race.id === selectedRace) || availableRaces[0];

  useEffect(() => {
    setIsLoaded(true);
    fetchPrediction(selectedRace);
  }, [selectedRace]);

  const getTeamColor = (teamName) => {
    const colors = {
      'Red Bull': '#0600EF',
      'Red Bull Racing': '#0600EF',
      'Ferrari': '#DC0000',
      'Mercedes': '#00D2BE',
      'McLaren': '#FF8000',
      'Aston Martin': '#006F62',
      'Alpine': '#0090FF',
      'Williams': '#005AFF',
      'AlphaTauri': '#2B4562',
      'RB': '#2B4562',
      'Alfa Romeo': '#900000',
      'Kick Sauber': '#52E252',
      'Haas': '#FFFFFF'
    };
    return colors[teamName] || '#FF0000';
  };

  const fetchPrediction = async (raceId) => {
    setLoading(true);
    setError(null);

    try {
      // Fetch race prediction
      const predictionResponse = await fetch(`http://localhost:8000/api/v1/predictions/pre-race/${raceId}`);
      if (!predictionResponse.ok) throw new Error('Failed to fetch prediction');
      const predictionData = await predictionResponse.json();

      // Fetch podium prediction
      const podiumResponse = await fetch(`http://localhost:8000/api/v1/predictions/podium/${raceId}`);
      if (!podiumResponse.ok) throw new Error('Failed to fetch podium');
      const podiumData = await podiumResponse.json();

      // Transform API data to component format
      const winnerName = predictionData.predictions?.winner || 'Unknown';

      // Find winner's team from podium data
      const winnerInfo = podiumData.podium_probabilities?.find(p => p.driver === winnerName);
      const winnerTeam = winnerInfo?.team || 'Unknown Team';

      // Format podium data
      const formattedPodium = podiumData.podium_probabilities?.slice(0, 3).map((p, index) => ({
        position: index + 1,
        driver: p.driver,
        team: p.team,
        probability: Math.round(p.podium_probability * 100),
        color: getTeamColor(p.team)
      })) || [];

      setPrediction({
        winner: winnerName,
        team: winnerTeam,
        confidence: Math.round((predictionData.confidence || 0) * 100),
        podium: formattedPodium
      });

    } catch (err) {
      console.error('Error fetching prediction:', err);
      // Use mock data as fallback
      setPrediction({
        winner: 'Max Verstappen',
        team: 'Red Bull Racing',
        confidence: 78,
        podium: [
          { position: 1, driver: 'Max Verstappen', team: 'Red Bull', probability: 35, color: '#0600EF' },
          { position: 2, driver: 'Charles Leclerc', team: 'Ferrari', probability: 28, color: '#DC0000' },
          { position: 3, driver: 'Lewis Hamilton', team: 'Mercedes', probability: 22, color: '#00D2BE' }
        ]
      });
      setError('Using demo predictions - API not available');
    } finally {
      setLoading(false);
    }
  };

  const handleRaceChange = (e) => {
    setSelectedRace(e.target.value);
  };

  const weather = {
    temperature: 28,
    humidity: 45,
    windSpeed: 12,
    conditions: 'Clear',
    icon: '☀️'
  };

  const stats = {
    modelAccuracy: 87,
    fanPredictions: 1234,
    racesAnalyzed: 340,
    liveUsers: 89
  };

  return (
    <div className={`dashboard ${isLoaded ? 'loaded' : ''}`}>
      {/* Hero Section */}
      <div className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">
            <span className="title-line">AI-Powered</span>
            <span className="title-line gradient-text">F1 Race Predictions</span>
          </h1>
          <p className="hero-subtitle">
            Real-time machine learning predictions for Formula 1 racing
          </p>
        </div>
        <div className="hero-bg-pattern"></div>
      </div>

      <div className="dashboard-container">
        {/* Race Selector */}
        <section className="race-selector-section">
          <div className="selector-header">
            <h2 className="selector-title">
              <span className="title-icon">🏎️</span>
              Select Grand Prix
            </h2>
            {error && <div className="error-message">{error}</div>}
          </div>

          <div className="race-selector-card glass-card">
            <select
              value={selectedRace}
              onChange={handleRaceChange}
              className="race-select"
              disabled={loading}
            >
              {availableRaces.map(race => (
                <option key={race.id} value={race.id}>
                  {race.flag} {race.name} - {race.date}
                </option>
              ))}
            </select>

            {loading && (
              <div className="loading-indicator">
                <div className="spinner"></div>
                <span>Loading prediction...</span>
              </div>
            )}
          </div>
        </section>

        {/* Race Details Card */}
        <section className="next-race-section">
          <div className="section-header">
            <h2 className="section-title">
              <span className="title-icon">🏁</span>
              Race Details
            </h2>
          </div>

          <div className="race-card glass-card">
            <div className="race-card-header">
              <div className="race-flag">{currentRace.flag}</div>
              <div className="race-details">
                <h3 className="race-name">{currentRace.name}</h3>
                <p className="race-circuit">{currentRace.circuit}</p>
              </div>
            </div>

            <div className="race-info-grid">
              <div className="info-item">
                <span className="info-label">Date</span>
                <span className="info-value">{currentRace.date}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Country</span>
                <span className="info-value">{currentRace.country}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Status</span>
                <span className="info-value">Upcoming</span>
              </div>
            </div>
          </div>
        </section>

        {/* Winner Prediction */}
        <section className="prediction-section">
          <div className="section-header">
            <h2 className="section-title">
              <span className="title-icon">🏆</span>
              Predicted Winner
            </h2>
          </div>

          <div className="winner-card glass-card">
            <div className="winner-content">
              <div className="winner-badge">
                <div className="trophy-icon">🏆</div>
              </div>
              <h3 className="winner-name">{prediction?.winner}</h3>
              <p className="winner-team">{prediction?.team}</p>

              <div className="confidence-meter">
                <div className="confidence-label">
                  <span>Confidence</span>
                  <span className="confidence-value">{prediction?.confidence || 0}%</span>
                </div>
                <div className="confidence-bar">
                  <div
                    className="confidence-fill"
                    style={{ width: `${prediction?.confidence || 0}%` }}
                  ></div>
                </div>
              </div>

              <Link to="/predictions" className="btn-primary">
                <span>View Detailed Analysis</span>
                <span className="btn-arrow">→</span>
              </Link>
            </div>
          </div>
        </section>

        {/* Podium Prediction */}
        <section className="podium-section">
          <div className="section-header">
            <h2 className="section-title">
              <span className="title-icon">🥇</span>
              Podium Prediction
            </h2>
          </div>

          <div className="podium-grid">
            {prediction?.podium?.map((driver, index) => (
              <div
                key={driver.position}
                className="podium-card glass-card"
                style={{
                  animationDelay: `${index * 0.1}s`,
                  borderTop: `3px solid ${driver.color || '#e10600'}`
                }}
              >
                <div className="podium-position" style={{ background: driver.color || '#e10600' }}>
                  P{driver.position}
                </div>
                <div className="podium-driver-info">
                  <h4 className="podium-driver-name">{driver.driver}</h4>
                  <p className="podium-team">{driver.team}</p>
                </div>
                <div className="podium-probability">
                  <div className="probability-circle">
                    <svg viewBox="0 0 36 36" className="circular-chart">
                      <path
                        className="circle-bg"
                        d="M18 2.0845
                          a 15.9155 15.9155 0 0 1 0 31.831
                          a 15.9155 15.9155 0 0 1 0 -31.831"
                      />
                      <path
                        className="circle"
                        strokeDasharray={`${driver.probability}, 100`}
                        d="M18 2.0845
                          a 15.9155 15.9155 0 0 1 0 31.831
                          a 15.9155 15.9155 0 0 1 0 -31.831"
                        style={{ stroke: driver.color || '#e10600' }}
                      />
                      <text x="18" y="20.35" className="percentage">{driver.probability}%</text>
                    </svg>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Weather & Stats Grid */}
        <div className="info-grid">
          {/* Weather Card */}
          <section className="weather-section">
            <div className="section-header">
              <h2 className="section-title">
                <span className="title-icon">🌤️</span>
                Weather Forecast
              </h2>
            </div>

            <div className="weather-card glass-card">
              <div className="weather-icon-large">{weather.icon}</div>
              <div className="weather-temp">{weather.temperature}°C</div>
              <div className="weather-condition">{weather.conditions}</div>

              <div className="weather-details">
                <div className="weather-detail-item">
                  <span className="detail-label">Humidity</span>
                  <span className="detail-value">{weather.humidity}%</span>
                </div>
                <div className="weather-detail-item">
                  <span className="detail-label">Wind</span>
                  <span className="detail-value">{weather.windSpeed} km/h</span>
                </div>
              </div>
            </div>
          </section>

          {/* Stats Cards */}
          <section className="stats-section">
            <div className="section-header">
              <h2 className="section-title">
                <span className="title-icon">📊</span>
                Platform Stats
              </h2>
            </div>

            <div className="stats-grid">
              <div className="stat-card glass-card">
                <div className="stat-icon">🎯</div>
                <div className="stat-value">{stats.modelAccuracy}%</div>
                <div className="stat-label">Model Accuracy</div>
              </div>

              <div className="stat-card glass-card">
                <div className="stat-icon">👥</div>
                <div className="stat-value">{stats.fanPredictions.toLocaleString()}</div>
                <div className="stat-label">Fan Predictions</div>
              </div>

              <div className="stat-card glass-card">
                <div className="stat-icon">🏎️</div>
                <div className="stat-value">{stats.racesAnalyzed}</div>
                <div className="stat-label">Races Analyzed</div>
              </div>

              <div className="stat-card glass-card">
                <div className="stat-icon pulse">🔴</div>
                <div className="stat-value">{stats.liveUsers}</div>
                <div className="stat-label">Live Users</div>
              </div>
            </div>
          </section>
        </div>

        {/* Action Buttons */}
        <section className="actions-section">
          <div className="action-buttons">
            <Link to="/live" className="action-btn glass-card">
              <span className="btn-icon">📡</span>
              <span className="btn-text">
                <strong>Live Race</strong>
                <small>Real-time predictions</small>
              </span>
            </Link>

            <Link to="/predictions" className="action-btn glass-card">
              <span className="btn-icon">📈</span>
              <span className="btn-text">
                <strong>Full Analysis</strong>
                <small>Detailed insights</small>
              </span>
            </Link>

            <Link to="/leaderboard" className="action-btn glass-card">
              <span className="btn-icon">🏅</span>
              <span className="btn-text">
                <strong>Leaderboard</strong>
                <small>Top predictors</small>
              </span>
            </Link>
          </div>
        </section>
      </div>
    </div>
  );
}

export default Dashboard;
