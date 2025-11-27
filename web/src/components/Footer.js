import React from 'react';

const Footer = () => {
    return (
        <footer className="bg-white border-t border-gray-200 mt-12">
            <div className="container mx-auto px-4 py-8">
                <div className="flex flex-col md:flex-row justify-between items-center">
                    <div className="mb-4 md:mb-0">
                        <h3 className="text-lg font-bold text-gray-900">F1 Predictor</h3>
                        <p className="text-sm text-gray-500">AI-powered race outcome predictions</p>
                    </div>
                    <div className="flex space-x-6 text-sm text-gray-600">
                        <a href="#" className="hover:text-red-600">About</a>
                        <a href="#" className="hover:text-red-600">Methodology</a>
                        <a href="#" className="hover:text-red-600">API</a>
                        <a href="#" className="hover:text-red-600">Github</a>
                    </div>
                </div>
                <div className="mt-8 text-center text-xs text-gray-400">
                    <p>© 2024 F1 Race Outcome Predictor. Not affiliated with Formula 1 companies.</p>
                </div>
            </div>
        </footer>
    );
};

export default Footer;
