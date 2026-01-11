
import React from 'react';
import { Clock } from 'lucide-react';
import { useCountdownTimer } from '../../hooks/use-timer';

const TimerDisplay = ({ startTime, onExpire }) => {
  const { timeRemaining, expired, formatted } = useCountdownTimer(startTime);
  
  // Trigger expiry callback once
  React.useEffect(() => {
    if (expired && onExpire) {
      onExpire();
    }
  }, [expired, onExpire]);

  const getContainerClass = () => {
    const oneMinute = 60 * 1000;
    
    if (timeRemaining <= oneMinute) {
      return 'bg-red-500 text-white animate-pulse';
    }
    return 'bg-blue-500 text-white';
  };

  return (
    <div className={`flex items-center gap-2 px-3 py-1 rounded-full shadow-sm transition-colors duration-300 ${getContainerClass()}`}>
      <Clock className="w-4 h-4" />
      <span className="font-mono font-bold text-sm">{formatted}</span>
    </div>
  );
};

export default TimerDisplay;
