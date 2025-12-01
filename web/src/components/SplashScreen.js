import React, { useEffect, useState } from 'react';
import './SplashScreen.css';
import racingCar from '../assets/racing_car.png';

const SplashScreen = ({ onFinish }) => {
  const [visible, setVisible] = useState(true);
  const [exiting, setExiting] = useState(false);

  useEffect(() => {
    // Start exit animation slightly before unmounting
    const exitTimer = setTimeout(() => {
      setExiting(true);
    }, 2500);

    const finishTimer = setTimeout(() => {
      setVisible(false);
      if (onFinish) onFinish();
    }, 3000); // Total duration 3s

    return () => {
      clearTimeout(exitTimer);
      clearTimeout(finishTimer);
    };
  }, [onFinish]);

  if (!visible) return null;

  return (
    <div className={`splash-screen ${exiting ? 'slide-out' : ''}`}>
      <div className="speed-lines"></div>
      <div className="content">
        <div className="car-wrapper">
          <img src={racingCar} alt="F1 Car" className="racing-car" />
          <div className="motion-blur-effect"></div>
          <div className="smoke-container">
             {[...Array(8)].map((_, i) => (
                <div key={i} className={`smoke-particle particle-${i}`}></div>
             ))}
          </div>
        </div>
        <h2 className="loading-text">INITIALIZING RACE SYSTEMS...</h2>
      </div>
    </div>
  );
};

export default SplashScreen;
