import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppContext } from '../../contexts/AppContext';
import { ChevronLeft, Info, Check } from 'lucide-react';
import { AvailabilityMode } from '../../data/mockData';
import Counter from '../../components/common/Counter';

export default function BrownModeSettings() {
  const navigate = useNavigate();
  const { setAvailabilityMode, currentUser } = useAppContext();
  const [hour, setHour] = useState(16); // 4 PM
  const [minute, setMinute] = useState(0);

  const wasActive = currentUser?.availabilityMode === AvailabilityMode.BROWN;

  const handleActivate = () => {
    setAvailabilityMode(AvailabilityMode.BROWN, { 
      timedHour: hour,
      timedMinute: minute,
      timezoneOffset: new Date().getTimezoneOffset()
    });
    
    navigate('/profile');
  };

  const handleDeactivate = () => {
    setAvailabilityMode(AvailabilityMode.GREEN, {});
    navigate('/profile');
  };

  const formatTime = (h, m) => {
    const period = h >= 12 ? 'PM' : 'AM';
    const displayHour = h % 12 || 12;
    return `${displayHour}:${String(m).padStart(2, '0')} ${period}`;
  };

  const handleHourChange = (newHour) => {
    // Wrapping logic handled in parent or custom incrementers
    setHour(newHour);
  };
  
  const incrementHour = () => {
     setHour(h => h === 23 ? 0 : h + 1);
  };
  
  const decrementHour = () => {
     setHour(h => h === 0 ? 23 : h - 1);
  };
  
  const incrementMinute = () => {
     setMinute(m => {
        const next = m + 15;
        return next >= 60 ? 0 : next;
     });
  };
  
  const decrementMinute = () => {
     setMinute(m => {
        const prev = m - 15;
        return prev < 0 ? 45 : prev;
     });
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
            <h1 className="text-xl font-semibold">Timed Mode</h1>
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
        <div className="w-20 h-20 mx-auto bg-amber-100 rounded-full flex items-center justify-center text-5xl mb-4">
          🟤
        </div>
        <p className="text-gray-600 max-w-sm mx-auto">
          Set the time when messaging will CLOSE
        </p>
      </div>

      <div className="px-4">
        <label className="block text-sm font-medium text-gray-700 mb-6 text-center">
          Closes at (24-hour format)
        </label>
        
        <div className="space-y-8 flex flex-col items-center">
          <Counter
             label={`Hour (${hour >= 12 ? 'PM' : 'AM'})`}
             value={hour}
             onChange={setHour} // fallback
             onIncrement={incrementHour}
             onDecrement={decrementHour}
          />
          
          <Counter
             label="Minute"
             value={minute}
             onChange={setMinute} // fallback
             onIncrement={incrementMinute}
             onDecrement={decrementMinute}
             displayValue={String(minute).padStart(2, '0')}
          />
        </div>
        
        <p className="text-lg font-bold text-gray-900 mt-8 text-center bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
           Closes at: {formatTime(hour, minute)}
        </p>
      </div>

      <div className="mx-4 mt-8 bg-amber-50 border border-amber-200 rounded-xl p-4 flex gap-3">
        <Info className="w-5 h-5 text-amber-700 flex-shrink-0 mt-0.5" />
        <p className="text-sm text-amber-900">
          Messaging will be disabled at this time every day. Available until then.
        </p>
      </div>

      <div className="px-4 mt-8 space-y-3">
        <button
          onClick={handleActivate}
          className="w-full py-4 bg-amber-700 hover:bg-amber-800 text-white rounded-xl font-semibold shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-2"
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
