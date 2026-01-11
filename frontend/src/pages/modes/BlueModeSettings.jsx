import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppContext } from '../../contexts/AppContext';
import { ChevronLeft, Info, Check, Calendar } from 'lucide-react';
import { AvailabilityMode } from '../../data/mockData';
import Counter from '../../components/common/Counter';

export default function BlueModeSettings() {
  const navigate = useNavigate();
  const { setAvailabilityMode, currentUser } = useAppContext();
  
  // Initialize with tomorrow or current setting
  const getInitialDate = () => {
     if (currentUser?.availability?.openDate) {
        return new Date(currentUser.availability.openDate);
     }
     const d = new Date();
     d.setDate(d.getDate() + 1); // Default to tomorrow
     return d;
  };

  const [selectedDate, setSelectedDate] = useState(getInitialDate());
  const [showDatePicker, setShowDatePicker] = useState(false);

  const wasActive = currentUser?.availabilityMode === AvailabilityMode.BLUE;

  const handleActivate = () => {
    // Convert to ISO string for storage
    const dateStr = selectedDate.toISOString().split('T')[0];
    setAvailabilityMode(AvailabilityMode.BLUE, { openDate: dateStr });
    navigate('/profile');
  };

  const handleDeactivate = () => {
    setAvailabilityMode(AvailabilityMode.GREEN, {});
    navigate('/profile');
  };
  
  const formatDate = (date) => {
     return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric', 
        year: 'numeric' 
     });
  };

  const handleIncrement = () => {
     const next = new Date(selectedDate);
     next.setDate(next.getDate() + 1);
     setSelectedDate(next);
  };

  const handleDecrement = () => {
     const prev = new Date(selectedDate);
     prev.setDate(prev.getDate() - 1);
     
     // Only allow future dates (Tomorrow and beyond)
     const tomorrow = new Date();
     tomorrow.setDate(tomorrow.getDate() + 1);
     tomorrow.setHours(0,0,0,0);
     
     if (prev >= tomorrow) {
        setSelectedDate(prev);
     }
  };
  
  const isPast = (d) => {
     const tomorrow = new Date();
     tomorrow.setDate(tomorrow.getDate() + 1);
     tomorrow.setHours(0,0,0,0);
     return d < tomorrow;
  };

  return (
    <div className="min-h-screen bg-gray-50 pb-24">
      {/* Header */}
      <div className="sticky top-0 z-10 bg-white border-b border-gray-200">
        <div className="px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button 
              onClick={() => navigate('/profile')}
              className="p-2 hover:bg-gray-100 rounded-full"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            <h1 className="text-xl font-semibold">Open Mode</h1>
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
        <div className="w-20 h-20 mx-auto bg-blue-100 rounded-full flex items-center justify-center text-5xl mb-4">
          🔵
        </div>
        <p className="text-gray-600 max-w-sm mx-auto">
          Set the date when you&apos;ll be available for messages
        </p>
      </div>

      <div className="px-4 flex flex-col items-center">
        <Counter
           label="Available from date"
           value={0} // Dummy
           onChange={() => {}} // Dummy
           displayValue={formatDate(selectedDate)}
           onIncrement={handleIncrement}
           onDecrement={handleDecrement}
           canDecrease={!isPast(new Date(selectedDate.getTime() - 86400000))} // Check if yesterday is past
        />
        
        <button
          onClick={() => setShowDatePicker(!showDatePicker)}
          className="mt-6 flex items-center gap-2 text-blue-600 font-medium hover:bg-blue-50 px-4 py-2 rounded-lg transition-colors"
        >
          <Calendar className="w-5 h-5" />
          {showDatePicker ? 'Hide Calendar' : 'Pick from Calendar'}
        </button>

        {showDatePicker && (
          <input
            type="date"
            value={selectedDate.toISOString().split('T')[0]}
            onChange={(e) => {
              if (e.target.value) {
                 const newDate = new Date(e.target.value);
                 // Enforce tomorrow as minimum
                 const tomorrow = new Date();
                 tomorrow.setDate(tomorrow.getDate() + 1);
                 tomorrow.setHours(0,0,0,0);
                 
                 // Reset time part of newDate for accurate comparison
                 // (Date from input is usually UTC midnight or local midnight depending on parsing, 
                 // but let's be safe)
                 // Actually new Date(string) from yyyy-mm-dd works in UTC usually. 
                 // Let's use simple string comparison for safety or ensure date object comparison is robust.
                 
                 if (newDate < tomorrow) {
                     setSelectedDate(tomorrow);
                 } else {
                     setSelectedDate(newDate);
                 }
                 setShowDatePicker(false);
              }
            }}
            min={(() => {
                const d = new Date();
                d.setDate(d.getDate() + 1);
                return d.toISOString().split('T')[0];
            })()}
            className="mt-4 w-full max-w-xs p-3 border-2 border-blue-500 rounded-xl"
          />
        )}
      </div>

      <div className="mx-4 mt-8 bg-blue-50 border border-blue-200 rounded-xl p-4 flex gap-3">
        <Info className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
        <p className="text-sm text-blue-900">
          You&apos;ll automatically become available on this date. Others will see 
          &quot;Available from {formatDate(selectedDate)}&quot;
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
