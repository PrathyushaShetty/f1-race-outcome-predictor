import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Header = () => {
  const location = useLocation();

  const navigation = [
    { name: 'Dashboard', href: '/', current: location.pathname === '/' },
    { name: 'Live Race', href: '/live', current: location.pathname === '/live' },
    { name: 'Predictions', href: '/predictions', current: location.pathname === '/predictions' },
    { name: 'Leaderboard', href: '/leaderboard', current: location.pathname === '/leaderboard' },
  ];

  return (
    <header className="bg-red-600 shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center py-4">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <div className="text-white text-2xl font-bold">
              🏎️ F1 Predictor
            </div>
          </Link>

          {/* Navigation */}
          <nav className="hidden md:flex space-x-8">
            {navigation.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  item.current
                    ? 'bg-red-700 text-white'
                    : 'text-red-100 hover:bg-red-500 hover:text-white'
                }`}
              >
                {item.name}
              </Link>
            ))}
          </nav>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button className="text-white hover:text-red-200">
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
