
import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAppContext } from '../contexts/AppContext';
import { AvailabilityMode } from '../data/mockData';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Calendar } from '../components/ui/calendar'; // shadcn calendar
import ModeIndicator from '../components/availability/ModeIndicator';

const ModeSettingsPage = () => {
  const { modeName } = useParams();
  const navigate = useNavigate();
  const { setAvailabilityMode, currentUser } = useAppContext();
  
  // Local state for forms
  const [date, setDate] = useState(new Date());
  const [duration, setDuration] = useState(60);
  const [maxContacts, setMaxContacts] = useState(5);
  const [time, setTime] = useState("09:00");

  const handleSubmit = () => {
    let settings = {};
    
    switch (modeName) {
      case AvailabilityMode.BLUE:
        settings = { openDate: date.toISOString() };
        break;
      case AvailabilityMode.YELLOW:
        settings = { laterMinutes: duration };
        break;
      case AvailabilityMode.ORANGE:
        settings = { maxContact: parseInt(maxContacts) || 5, currentContacts: 0 };
        break;
      case AvailabilityMode.BROWN:
        const [h, m] = time.split(':');
        settings = { timedHour: parseInt(h), timedMinute: parseInt(m) };
        break;
      default:
        break;
    }

    setAvailabilityMode(modeName, settings);
    // Go back to profile
    navigate('/profile');
  };

  const renderContent = () => {
    switch (modeName) {
      case AvailabilityMode.BLUE:
        return (
          <div className="space-y-4">
             <p className="text-gray-500">Set the date when you'll be available for messages.</p>
             <div className="flex justify-center bg-white p-4 rounded-xl border border-gray-100">
               <Calendar 
                 mode="single"
                 selected={date}
                 onSelect={setDate}
                 className="rounded-md border"
                 disabled={(date) => date < new Date()}
               />
             </div>
          </div>
        );
      case AvailabilityMode.YELLOW:
        return (
          <div className="space-y-4">
            <p className="text-gray-500">Set how long you'll be available for messages.</p>
            <div className="grid grid-cols-2 gap-3">
              {[15, 30, 60, 120, 240].map(m => (
                <div 
                  key={m}
                  onClick={() => setDuration(m)}
                  className={`p-3 rounded-lg border text-center cursor-pointer ${duration === m ? 'bg-mode-yellow text-white border-mode-yellow' : 'bg-white border-gray-200'}`}
                >
                  {m} minutes
                </div>
              ))}
            </div>
          </div>
        );
      case AvailabilityMode.ORANGE:
        return (
          <div className="space-y-4">
            <p className="text-gray-500">Limit the number of people who can message you.</p>
            <div className="space-y-2">
              <Label>Maximum Contacts</Label>
              <Input 
                type="number" 
                value={maxContacts} 
                onChange={e => setMaxContacts(e.target.value)}
                min="1"
                max="100"
              />
            </div>
          </div>
        );
      case AvailabilityMode.BROWN:
        return (
          <div className="space-y-4">
            <p className="text-gray-500">Set specific time of day when you'll be available.</p>
            <Input 
              type="time" 
              value={time} 
              onChange={e => setTime(e.target.value)}
              className="text-2xl p-4 h-16 text-center"
            />
          </div>
        );
      case AvailabilityMode.RED:
        return (
          <div className="bg-red-50 p-4 rounded-xl text-red-800 border border-red-100">
            <p className="font-bold">⚠️ WARNING</p>
            <p className="text-sm mt-2">This will completely lock your messaging. Nobody can contact you until you unlock manually.</p>
          </div>
        );
      case AvailabilityMode.GREEN:
        return (
           <div className="bg-green-50 p-4 rounded-xl text-green-800 border border-green-100">
            <p className="font-bold">✅ Go Online</p>
            <p className="text-sm mt-2">You will be available to everyone immediately.</p>
          </div>
        );
      case AvailabilityMode.GRAY:
        return (
           <div className="bg-gray-100 p-4 rounded-xl text-gray-800 border border-gray-200">
            <p className="font-bold">⏸️ Pause</p>
            <p className="text-sm mt-2">Messaging paused temporarily. Similar to locked mode but softer.</p>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="p-4 min-h-screen bg-gray-50 flex flex-col">
      <h1 className="text-xl font-bold mb-6 capitalize">{modeName} Mode Settings</h1>
      
      <div className="flex-1">
        {renderContent()}
      </div>

      <Button onClick={handleSubmit} className="w-full mt-6 h-12 text-lg bg-gray-900 text-white hover:bg-gray-800">
        Confirm & Activate
      </Button>
    </div>
  );
};

export default ModeSettingsPage;
