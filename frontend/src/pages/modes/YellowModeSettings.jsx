import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppContext } from '../../contexts/AppContext';
import { ChevronLeft, Info, Check } from 'lucide-react';
import { AvailabilityMode } from '../../data/mockData';
import Counter from '../../components/common/Counter';

export default function YellowModeSettings() {
  const navigate = useNavigate();
  const { setAvailabilityMode, currentUser } = useAppContext();
  const [duration, setDuration] = useState(60); // minutes
  const [customDuration, setCustomDuration] = useState(''); // Not used with Counter, keeping for safety if switching back but mostly replacing logic
  const [useCustom, setUseCustom] = useState(false); // Not needed with Counter as everything is custom/counter based

  const wasActive = currentUser?.availabilityMode === AvailabilityMode.YELLOW;

  const handleActivate = () => {
    // AppContext handles validation and toast
    setAvailabilityMode(AvailabilityMode.YELLOW, { 
      laterMinutes: duration,
      laterStartTime: Date.now() 
    });
    
    navigate('/profile');
  };

  const handleDeactivate = () => {
    setAvailabilityMode(AvailabilityMode.GREEN, {});
    navigate('/profile');
  };

  // Helper for step logic
  const getStep = (val) => {
    if (val < 60) return 5;
    if (val < 120) return 15;
    return 30;
  };

  // Custom increment/decrement for variable steps
  const handleIncrement = () => {
    const step = getStep(duration);
    setDuration(Math.min(1440, duration + step));
  };

  const handleDecrement = () => {
    // Determine step based on *previous* value range? 
    // Actually, if we are at 60, step is 15 (for next), but going down we want 5?
    // Let's use current value to determine step downwards too.
    let step = 30;
    if (duration <= 60) step = 5;
    else if (duration <= 120) step = 15;
    
    setDuration(Math.max(5, duration - step));
  };

  const formatDuration = (mins) => {
    if (mins < 60) return `${mins} minutes`;
    const hours = Math.floor(mins / 60);
    const remaining = mins % 60;
    if (remaining === 0) return `${hours} hour${hours > 1 ? 's' : ''}`;
    return `${hours}h ${remaining}m`;
  };

  return (
    <div className="min-h-screen bg-gray-50 pb-24">
      {/* Header */}
      <div className="sticky top-0 z-10 bg-white border-b border-gray-200">
        <div className="px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button onClick={() => navigate('/profile')} className="p-2 hover:bg-gray-100 rounded-full">
              <ChevronLeft className="w-5 h-5" />
            </button>
            <h1 className="text-xl font-semibold">Later Mode</h1>
          </div>

          {wasActive ? (
            <div className="flex items-center gap-1 px-3 py-1 bg-green-500 text-white rounded-full shadow-sm">
              <Check className="w-3 h-3" />
              <span className="text-xs font-bold uppercase tracking-wide">ACTIVATED</span>
            </div>
          ) : (
            <div className="px-3 py-1 bg-gray-300 text-gray-600 rounded-full">
              <span className="text-xs font-bold uppercase tracking-wide">DEACTIVATED</span>
            </div>
          )}
        </div>
      </div>

      <div className="px-6 py-8 text-center">
        <div className="w-20 h-20 mx-auto bg-yellow-100 rounded-full flex items-center justify-center text-5xl mb-4">
          🟡
        </div>
        <p className="text-gray-600 max-w-sm mx-auto">
          Set how long you&apos;ll be available for messages
        </p>
      </div>

      <div className="px-4 flex flex-col items-center">
        <Counter
          label="Duration (minutes)"
          value={duration}
          onChange={setDuration} // Not strictly used due to custom handlers but good for types
          onIncrement={handleIncrement}
          onDecrement={handleDecrement}
          canDecrease={duration > 5}
          canIncrease={duration < 1440}
        />
        
        <p className="text-lg font-medium text-gray-900 mt-4 text-center">
           {formatDuration(duration)}
        </p>
        
        <div className="flex gap-2 mt-6 flex-wrap justify-center">
          {[15, 30, 60, 120].map(mins => (
             <button 
               key={mins}
               onClick={() => setDuration(mins)} 
               className={`px-3 py-1 text-sm border rounded hover:bg-gray-50 ${duration === mins ? 'bg-yellow-100 border-yellow-500 font-semibold' : ''}`}
             >
               {mins < 60 ? `${mins} min` : `${mins/60} hr`}
             </button>
          ))}
        </div>
      </div>

      <div className="mx-4 mt-8 bg-yellow-50 border border-yellow-200 rounded-xl p-4 flex gap-3">
        <Info className="w-5 h-5 text-yellow-700 flex-shrink-0 mt-0.5" />
        <p className="text-sm text-yellow-900">
          Timer starts when you activate. You&apos;ll switch to Pause mode automatically when time expires.
        </p>
      </div>

      <div className="px-4 mt-8 space-y-3">
        <button
          onClick={handleActivate}
          className="w-full py-4 bg-green-600 hover:bg-green-700 text-white rounded-xl font-semibold shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-2"
        >
          <Check className="w-5 h-5" />
          {wasActive ? 'UPDATE ACTIVATION' : 'ACTIVATE MODE'}
        </button>

        {wasActive && (
          <button
            onClick={handleDeactivate}
            className="w-full py-4 bg-red-500 text-white rounded-xl font-semibold hover:bg-red-600 transition-all shadow-sm"
          >
            DEACTIVATE MODE
          </button>
        )}
      </div>
    </div>
  );
}
