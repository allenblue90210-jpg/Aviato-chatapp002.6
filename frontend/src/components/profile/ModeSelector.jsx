
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { AvailabilityMode } from '../../data/mockData';
import ModeIndicator from '../availability/ModeIndicator';

const modes = [
  { id: AvailabilityMode.BLUE, label: 'Open Mode', desc: 'Available from specific date', color: 'bg-mode-blue' },
  { id: AvailabilityMode.YELLOW, label: 'Later Mode', desc: 'Available for limited duration', color: 'bg-mode-yellow' },
  { id: AvailabilityMode.ORANGE, label: 'Max Contact', desc: 'Limit number of contacts', color: 'bg-mode-orange' },
  { id: AvailabilityMode.GREEN, label: 'Available', desc: 'Online and ready to chat', color: 'bg-mode-green' },
  { id: AvailabilityMode.RED, label: 'Locked', desc: 'Completely unavailable', color: 'bg-mode-red' },
  { id: AvailabilityMode.GRAY, label: 'Pause', desc: 'Temporarily paused', color: 'bg-mode-gray' },
  { id: AvailabilityMode.BROWN, label: 'Timed Mode', desc: 'Available at specific time', color: 'bg-mode-brown' },
];

const ModeSelector = () => {
  const navigate = useNavigate();

  return (
    <div className="bg-gray-50 min-h-screen p-4">
      <h1 className="text-xl font-bold mb-6">Select Your Availability Mode</h1>
      
      <div className="grid gap-3">
        {modes.map((mode) => (
          <div 
            key={mode.id}
            onClick={() => navigate(`/profile/mode/${mode.id}`)}
            className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex items-center gap-4 cursor-pointer hover:shadow-md transition-all active:scale-[0.99]"
          >
            <ModeIndicator mode={mode.id} size="large" />
            <div className="flex-1">
              <h3 className="font-bold text-gray-900">{mode.label}</h3>
              <p className="text-sm text-gray-500">{mode.desc}</p>
            </div>
            <div className="text-gray-300">→</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ModeSelector;
