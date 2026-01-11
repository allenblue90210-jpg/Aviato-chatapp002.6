import React from 'react';
import { Minus, Plus } from 'lucide-react';

export default function Counter({ 
  value, 
  onChange, 
  min = -Infinity, 
  max = Infinity, 
  step = 1,
  label,
  onIncrement,
  onDecrement,
  displayValue,
  canIncrease: externalCanIncrease,
  canDecrease: externalCanDecrease
}) {
  
  const handleDecrease = () => {
    if (onDecrement) {
      onDecrement();
    } else {
      const newValue = Math.max(min, value - step);
      onChange(newValue);
    }
  };
  
  const handleIncrease = () => {
    if (onIncrement) {
      onIncrement();
    } else {
      const newValue = Math.min(max, value + step);
      onChange(newValue);
    }
  };
  
  // Logic for disable state
  // Use external props if provided, otherwise default logic
  const canDecrease = externalCanDecrease !== undefined 
    ? externalCanDecrease 
    : (typeof value === 'number' ? value > min : true);
    
  const canIncrease = externalCanIncrease !== undefined 
    ? externalCanIncrease 
    : (typeof value === 'number' ? value < max : true);
  
  return (
    <div className="flex flex-col items-center gap-2">
      {label && (
        <label className="text-sm font-medium text-gray-700">
          {label}
        </label>
      )}
      
      <div className="flex items-center gap-4">
        {/* Minus Button */}
        <button
          onClick={handleDecrease}
          disabled={!canDecrease}
          className={`
            w-12 h-12 flex items-center justify-center
            rounded-lg border-2 font-bold text-xl
            transition-all duration-200
            ${canDecrease 
              ? 'border-blue-500 text-blue-600 hover:bg-blue-50 active:scale-95' 
              : 'border-gray-300 text-gray-400 cursor-not-allowed'
            }
          `}
        >
          <Minus className="w-6 h-6" />
        </button>
        
        {/* Display Value */}
        <div className="min-w-[80px] h-12 flex items-center justify-center px-2">
          <span className="text-3xl font-bold text-gray-900 whitespace-nowrap">
            {displayValue || value}
          </span>
        </div>
        
        {/* Plus Button */}
        <button
          onClick={handleIncrease}
          disabled={!canIncrease}
          className={`
            w-12 h-12 flex items-center justify-center
            rounded-lg border-2 font-bold text-xl
            transition-all duration-200
            ${canIncrease 
              ? 'border-blue-500 text-blue-600 hover:bg-blue-50 active:scale-95' 
              : 'border-gray-300 text-gray-400 cursor-not-allowed'
            }
          `}
        >
          <Plus className="w-6 h-6" />
        </button>
      </div>
    </div>
  );
}
