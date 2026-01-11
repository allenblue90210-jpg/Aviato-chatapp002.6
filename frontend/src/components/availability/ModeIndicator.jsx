
import React from 'react';
import { getModeColor } from '../../utils/availability';

const ModeIndicator = ({ mode, size = 'medium', className = '' }) => {
  const sizeClasses = {
    small: 'w-3 h-3',
    medium: 'w-4 h-4',
    large: 'w-6 h-6'
  };
  
  const color = getModeColor(mode);
  
  return (
    <div 
      className={`rounded-full border-2 border-white shadow-sm ${sizeClasses[size]} ${className}`}
      style={{ backgroundColor: color }}
      title={`Mode: ${mode}`}
    />
  );
};

export default ModeIndicator;
