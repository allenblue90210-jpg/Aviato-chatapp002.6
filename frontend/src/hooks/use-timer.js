
import { useState, useEffect } from 'react';

export function useCountdownTimer(startTime) {
  const [now, setNow] = useState(Date.now());
  
  useEffect(() => {
    if (!startTime) return;
    
    const interval = setInterval(() => {
      setNow(Date.now());
    }, 1000);
    
    return () => clearInterval(interval);
  }, [startTime]);
  
  if (!startTime) {
    return { 
      timeRemaining: 0, 
      expired: false, 
      formatted: '00:02:00' 
    };
  }
  
  // 2 MINUTES FOR EVERYONE
  const duration = 2 * 60 * 1000;
  
  const elapsed = now - startTime;
  const remaining = Math.max(0, duration - elapsed);
  const expired = remaining === 0;
  
  const hours = Math.floor(remaining / 3600000);
  const minutes = Math.floor((remaining % 3600000) / 60000);
  const seconds = Math.floor((remaining % 60000) / 1000);
  
  const formatted = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
  
  return { timeRemaining: remaining, expired, formatted };
}
