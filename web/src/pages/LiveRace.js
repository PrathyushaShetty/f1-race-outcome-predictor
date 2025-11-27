import React from 'react';

const LiveRace = () => {
    return (
        <div className="space-y-6">
            <h1 className="text-3xl font-bold text-gray-900">Live Race Analysis</h1>
            <div className="bg-white p-12 rounded-xl shadow-sm border border-gray-100 text-center">
                <div className="inline-block p-4 rounded-full bg-gray-100 mb-4">
                    <span className="text-4xl">🏁</span>
                </div>
                <h2 className="text-xl font-bold text-gray-800 mb-2">No Live Race</h2>
                <p className="text-gray-500">Waiting for the next session to begin.</p>
            </div>
        </div>
    );
};

export default LiveRace;
