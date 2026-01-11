import React from 'react';
import { AvailabilityMode } from '../../data/mockData';
import { getModeColor } from '../../utils/availability';

const ModeStatusBanner = ({ user }) => {
  if (!user) return null;

  const modeColor = getModeColor(user.availabilityMode);
  
  // Helper to format time
  const formatTime = (hour, minute) => {
    const period = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour % 12 || 12;
    const displayMinute = minute ? minute.toString().padStart(2, '0') : '00';
    return `${displayHour}:${displayMinute} ${period}`;
  };
  
  // Get banner text based on mode
  const getBannerText = () => {
    switch(user.availabilityMode) {
      case AvailabilityMode.GREEN:
        return `${user.name} is available now`;
      case AvailabilityMode.YELLOW:
        return `${user.name} is available for ${user.availability?.laterMinutes || 0} minutes`;
      case AvailabilityMode.ORANGE:
        if (user.availability?.currentContacts >= user.availability?.maxContact) {
          return `${user.name} has reached max contacts (${user.availability.currentContacts}/${user.availability.maxContact})`;
        }
        return `${user.name} has ${user.availability?.maxContact - user.availability?.currentContacts || 0} contact slots remaining`;
      case AvailabilityMode.BLUE:
        if (user.availability?.openDate) {
          const date = new Date(user.availability.openDate).toLocaleDateString();
          return `${user.name} will be available on ${date}`;
        }
        return `${user.name} will be available on a specific date`;
      case AvailabilityMode.RED:
        return `${user.name} has locked messaging`;
      case AvailabilityMode.GRAY:
        return `${user.name} has paused messaging`;
      case AvailabilityMode.BROWN:
        if (user.availability?.timedHour !== null) {
          const timeStr = formatTime(user.availability.timedHour, user.availability.timedMinute || 0);
          return `${user.name} is available at ${timeStr} daily`;
        }
        return `${user.name} has timed availability`;
      default:
        return `${user.name}'s availability status`;
    }
  };
  
  // Get banner style based on availability
  const getBannerStyle = () => {
    const canMessage = [AvailabilityMode.GREEN, AvailabilityMode.YELLOW, AvailabilityMode.ORANGE].includes(user.availabilityMode);
    
    if (user.availabilityMode === AvailabilityMode.ORANGE && 
        user.availability?.currentContacts >= user.availability?.maxContact) {
      return 'bg-orange-50 border-orange-200 text-orange-800';
    }
    
    return canMessage 
      ? 'bg-green-50 border-green-200 text-green-800' 
      : 'bg-gray-50 border-gray-200 text-gray-700';
  };

  return (
    <div className={`mx-4 my-3 px-4 py-3 rounded-lg border ${getBannerStyle()} flex items-center gap-2.5 shadow-sm`}>
      <span
        className="w-2.5 h-2.5 rounded-full flex-shrink-0"
        style={{ backgroundColor: modeColor }}
      />
      <p className="text-xs font-medium flex-1">
        {getBannerText()}
      </p>
    </div>
  );
};

export default ModeStatusBanner;
